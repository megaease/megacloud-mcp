import secrets


def generate_name(prefix: str):
    token = secrets.token_hex(8)
    name = f"{prefix}_{token}"
    return name
