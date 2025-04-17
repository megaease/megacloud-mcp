from enum import Enum
from typing import List

from mcp.server import Server
from mcp.types import TextContent, Tool

from . import apis
from . import utils


class MegaCloudTools(str, Enum):
    ListHosts = "list_available_hosts"
    ListMiddlewareTypes = "list_middleware_types"
    ListMiddlewareInstances = "list_middleware_instances"


async def list_tools() -> list[Tool]:
    return [
        Tool(
            name=MegaCloudTools.ListHosts,
            description="List all available hosts that can be used to deploy middleware.",
            inputSchema={},
        ),
        Tool(
            name=MegaCloudTools.ListMiddlewareTypes,
            description="List all middleware types that can be deployed.",
            inputSchema={},
        ),
        Tool(
            name=MegaCloudTools.ListMiddlewareInstances,
            description="List all middleware instances that are currently deployed.",
            inputSchema={},
        ),
    ]


async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    match name:
        case MegaCloudTools.ListHosts:
            hosts = await apis.list_available_hosts()
            return utils.to_textcontent(hosts)
        case MegaCloudTools.ListMiddlewareTypes:
            middleware_types = await apis.list_available_middleware_type()
            return utils.to_textcontent(middleware_types)
        case MegaCloudTools.ListMiddlewareInstances:
            middleware_instances = await apis.list_current_middleware_instances()
            return utils.to_textcontent(middleware_instances)
    raise ValueError(f"Unknown tool name: {name}")
