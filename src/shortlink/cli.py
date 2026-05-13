import csv
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, col, select

from shortlink.config import get_settings
from shortlink.db import get_engine, init_db
from shortlink.models import HitDaily, Link
from shortlink.slugs import generate_slug

app = typer.Typer(help="shortlink admin CLI", no_args_is_help=True)
console = Console()


@app.callback()
def _root() -> None:
    """Group entrypoint — forces typer to keep subcommand routing on."""


def _validate_url(raw: str) -> str:
    """Parse the URL and reject anything that is not http(s)://host."""
    try:
        url = httpx.URL(raw)
    except (httpx.InvalidURL, TypeError) as exc:
        raise typer.BadParameter(f"invalid URL: {exc}") from None
    if url.scheme not in {"http", "https"}:
        raise typer.BadParameter("URL must be http:// or https://")
    if not url.host:
        raise typer.BadParameter("URL must include a host")
    return str(url)


@app.command("init")
def init() -> None:
    """Create the database file and tables at $SHORTLINK_DB_PATH."""
    init_db()
    typer.echo("database initialised")


@app.command("add")
def add(
    target: str = typer.Argument(..., help="The destination URL"),
    slug: str | None = typer.Option(None, "--slug", "-s", help="Custom slug"),
) -> None:
    """Add a new link. Generates a base62 slug if --slug is not given."""
    target = _validate_url(target)
    settings = get_settings()
    init_db()
    with Session(get_engine()) as session:
        if slug is None:
            for _ in range(10):
                candidate = generate_slug(settings.slug_length)
                if session.get(Link, candidate) is None:
                    slug = candidate
                    break
            else:
                raise typer.Exit(code=1)
        elif session.get(Link, slug) is not None:
            console.print(f"[red]slug already exists:[/red] {slug}")
            raise typer.Exit(code=1)
        link = Link(slug=slug, target=target)
        session.add(link)
        session.commit()
        console.print(f"[green]{settings.base_url}/{slug}[/green]  →  {target}")


@app.command("ls")
def ls() -> None:
    """List all links."""
    init_db()
    table = Table(title="links")
    table.add_column("slug", style="cyan", no_wrap=True)
    table.add_column("target", style="white")
    table.add_column("hits", justify="right", style="magenta")
    table.add_column("created", style="dim")
    with Session(get_engine()) as session:
        rows = session.exec(select(Link).order_by(col(Link.created_at).desc())).all()
    for r in rows:
        table.add_row(
            r.slug,
            r.target,
            str(r.hits),
            r.created_at.strftime("%Y-%m-%d"),
        )
    console.print(table)


@app.command("rm")
def rm(slug: str = typer.Argument(...)) -> None:
    """Remove a link by slug."""
    init_db()
    with Session(get_engine()) as session:
        link = session.get(Link, slug)
        if link is None:
            console.print(f"[red]no such slug:[/red] {slug}")
            raise typer.Exit(code=1)
        session.delete(link)
        session.commit()
        console.print(f"deleted [cyan]{slug}[/cyan]")


@app.command("rename")
def rename(
    old: str = typer.Argument(..., help="Existing slug"),
    new: str = typer.Argument(..., help="New slug"),
) -> None:
    """Rename a slug. Fails if the new slug already exists."""
    init_db()
    with Session(get_engine()) as session:
        link = session.get(Link, old)
        if link is None:
            console.print(f"[red]no such slug:[/red] {old}")
            raise typer.Exit(code=1)
        if session.get(Link, new) is not None:
            console.print(f"[red]slug already exists:[/red] {new}")
            raise typer.Exit(code=1)
        # sqlmodel forbids editing a primary key in place; delete + recreate.
        new_link = Link(
            slug=new,
            target=link.target,
            created_at=link.created_at,
            hits=link.hits,
        )
        session.delete(link)
        session.add(new_link)
        session.commit()
        console.print(f"renamed [cyan]{old}[/cyan] → [cyan]{new}[/cyan]")


@app.command("export")
def export_(path: Path = typer.Argument(..., help="Output CSV path")) -> None:
    """Dump every link to a CSV file."""
    init_db()
    with Session(get_engine()) as session:
        rows = session.exec(select(Link).order_by(col(Link.created_at))).all()
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["slug", "target", "created_at", "hits"])
        for r in rows:
            writer.writerow([r.slug, r.target, r.created_at.isoformat(), r.hits])
    console.print(f"exported [green]{len(rows)}[/green] links → {path}")


@app.command("import")
def import_(path: Path = typer.Argument(..., help="Input CSV path")) -> None:
    """Bulk-add links from a CSV produced by `shortlink export`."""
    init_db()
    added = 0
    skipped = 0
    with Session(get_engine()) as session, path.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            slug = row["slug"]
            if session.get(Link, slug) is not None:
                skipped += 1
                continue
            session.add(Link(slug=slug, target=row["target"]))
            added += 1
        session.commit()
    console.print(f"imported [green]{added}[/green], skipped [yellow]{skipped}[/yellow]")


@app.command("stats")
def stats(
    slug: str = typer.Argument(...),
    days: int = typer.Option(7, "--days", "-d", min=1, max=365),
) -> None:
    """Print a per-day hit histogram for the slug over the last N days."""
    init_db()
    today = datetime.now(UTC).date()
    start = today - timedelta(days=days - 1)
    with Session(get_engine()) as session:
        if session.get(Link, slug) is None:
            console.print(f"[red]no such slug:[/red] {slug}")
            raise typer.Exit(code=1)
        rows = session.exec(
            select(HitDaily)
            .where(HitDaily.slug == slug)
            .where(HitDaily.day >= start)
        ).all()
    counts = {r.day: r.count for r in rows}
    peak = max(counts.values(), default=0) or 1
    bar_width = 40
    for i in range(days):
        d = start + timedelta(days=i)
        c = counts.get(d, 0)
        bar = "█" * int(round(c / peak * bar_width))
        console.print(f"{d.isoformat()}  {c:>4}  [cyan]{bar}[/cyan]")


@app.command("health")
def health(
    timeout: float = typer.Option(5.0, "--timeout", help="Per-request timeout, seconds"),
) -> None:
    """HEAD-check every target URL; report dead links."""
    init_db()
    with Session(get_engine()) as session:
        links = session.exec(select(Link)).all()

    table = Table(title="health check")
    table.add_column("slug", style="cyan")
    table.add_column("target")
    table.add_column("status", justify="right")
    dead = 0
    with httpx.Client(follow_redirects=True, timeout=timeout) as client:
        for link in links:
            try:
                r = client.head(link.target)
                status = str(r.status_code)
                if r.status_code >= 400:
                    dead += 1
                    status = f"[red]{status}[/red]"
                else:
                    status = f"[green]{status}[/green]"
            except httpx.HTTPError as exc:
                status = f"[red]error: {type(exc).__name__}[/red]"
                dead += 1
            table.add_row(link.slug, link.target, status)
    console.print(table)
    if dead:
        console.print(f"[yellow]{dead} dead link(s)[/yellow]")
        raise typer.Exit(code=1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
