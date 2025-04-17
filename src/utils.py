import secrets
from typing import List, Sequence

from pydantic import BaseModel
from mcp.types import TextContent


def generate_name(prefix: str):
    token = secrets.token_hex(8)
    name = f"{prefix}_{token}"
    return name


def to_textcontent(model: BaseModel | Sequence[BaseModel]) -> List[TextContent]:
    if isinstance(model, Sequence) and not isinstance(model, BaseModel):
        return [
            TextContent(
                type="text",
                text=item.model_dump_json(),
            )
            for item in model
        ]
    else:
        return [
            TextContent(
                type="text",
                text=model.model_dump_json(),
            )
        ]
