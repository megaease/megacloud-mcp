import os
import httpx
from megacloud_mcp.settings import ENV_AUTHTOKEN


def get_header():
    token = os.getenv(ENV_AUTHTOKEN, "")
    if token == "":
        raise ValueError(f"Environment variable {ENV_AUTHTOKEN} not set")
    headers = {"Authorization": f"Bearer {token}"}
    return headers


def get_async_client():
    client = httpx.AsyncClient(headers=get_header())
    return client


def get_client():
    client = httpx.Client(headers=get_header())
    return client


client = get_client()
async_client = get_async_client()
