import secrets

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def generate_slug(length: int) -> str:
    if length < 1:
        raise ValueError("slug length must be >= 1")
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
