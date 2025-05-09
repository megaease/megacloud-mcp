import secrets
import time
from typing import Any, List
from datetime import datetime
from pydantic import BaseModel
from mcp.types import TextContent


def generate_name(prefix: str):
    token = secrets.token_hex(8)
    name = f"{prefix}_{token}"
    return name


def to_textcontent(model: Any) -> List[TextContent]:
    if isinstance(model, list) and len(model) > 0 and isinstance(model[0], BaseModel):
        return [
            TextContent(
                type="text",
                text=item.model_dump_json(),
            )
            for item in model
        ]
    elif isinstance(model, list):
        return [
            TextContent(
                type="text",
                text=f"{item}",
            )
            for item in model
        ]
    elif isinstance(model, BaseModel):
        return [
            TextContent(
                type="text",
                text=model.model_dump_json(),
            )
        ]
    else:
        return [
            TextContent(
                type="text",
                text=f"{model}",
            )
        ]


def from_unix_mill_to_datetime(unix_mill: int) -> str:
    dt = datetime.fromtimestamp(unix_mill / 1000.0)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def current_millis() -> int:
    return round(time.time() * 1000)


def get_start_end_time(interval_in_mins: int):
    end_time = current_millis()
    start_time = end_time - interval_in_mins * 60 * 1000
    return start_time, end_time
