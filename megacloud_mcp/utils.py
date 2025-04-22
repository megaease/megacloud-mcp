import secrets
from typing import Any, List, Sequence

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
