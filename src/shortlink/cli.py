import typer

from shortlink.db import init_db

app = typer.Typer(help="shortlink admin CLI", no_args_is_help=True)


@app.callback()
def _root() -> None:
    """Group entrypoint — forces typer to keep subcommand routing on."""


@app.command("init")
def init() -> None:
    """Create the database file and tables at $SHORTLINK_DB_PATH."""
    init_db()
    typer.echo("database initialised")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
