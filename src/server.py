from mcp.server import Server
from mcp.types import TextContent, Tool

from . import tools

server = Server("megacloud")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return await tools.list_tools()


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    return await tools.call_tool(name, arguments)
