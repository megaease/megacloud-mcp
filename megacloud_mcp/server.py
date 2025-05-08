import asyncio
from enum import Enum
from typing import List

from mcp.server import Server
from mcp.types import TextContent, Tool
from mcp.server.stdio import stdio_server

from megacloud_mcp import apis
from megacloud_mcp import utils
from megacloud_mcp import schema
from megacloud_mcp import middleware
from megacloud_mcp.log import logger


class MegaCloudTools(str, Enum):
    ListHosts = "list_available_hosts"
    ListMiddlewareTypes = "list_middleware_types"
    ListMiddlewareInstances = "list_middleware_instances"
    RestartMiddleware = "restart_middleware"
    StopMiddleware = "stop_middleware"
    StartMiddleware = "start_middleware"
    DeleteMiddleware = "delete_middleware"
    GetMiddlewareInfo = "get_middleware_info"
    GetMiddlewareStatus = "get_middleware_status"
    BackupMiddleware = "backup_middleware"
    ListMiddlewareInstanceNodes = "list_middleware_instance_nodes"
    RemoveMiddlewareInstanceNodes = "remove_middleware_instance_nodes"
    ListMiddlewareInstanceChangeEvents = "list_middleware_instance_change_events"
    ListMiddlewareInstanceAlertRules = "list_middleware_instance_alert_rules"
    ListMiddlewareInstanceSupportLogTypes = "list_middleware_type_support_log_types"
    ListMiddlewareInstanceLogs = "list_middleware_instance_logs"

    # redis
    CreateSingleRedisMiddleware = "create_single_redis_middleware"
    CreateRedisClusterMiddleware = "create_redis_cluster_middleware"
    AddRedisNodes = "add_redis_nodes"


async def change_middleware_state(arguments: dict, operation: int) -> List[TextContent]:
    arg = schema.MiddlewareNameSchema(**arguments)
    resp = await middleware.change_middleware_state(arg.middleware_instance_name, operation)
    return utils.to_textcontent(resp)


async def serve():
    server = Server("megacloud")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=MegaCloudTools.ListHosts,
                description="List all available hosts that can be used to deploy middleware.",
                inputSchema=schema.EmptySchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.ListMiddlewareTypes,
                description="List all middleware types.",
                inputSchema=schema.EmptySchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.ListMiddlewareInstances,
                description="List all middleware instances that are currently deployed.",
                inputSchema=schema.EmptySchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.RestartMiddleware,
                description="Restart a middleware instance.",
                inputSchema=schema.MiddlewareNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.StopMiddleware,
                description="Stop a middleware instance.",
                inputSchema=schema.MiddlewareNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.StartMiddleware,
                description="Start a middleware instance.",
                inputSchema=schema.MiddlewareNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.DeleteMiddleware,
                description="Delete a middleware instance.",
                inputSchema=schema.MiddlewareNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.GetMiddlewareInfo,
                description="Get all information of a middleware instance, like configs, nodes, etc.",
                inputSchema=schema.MiddlewareNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.GetMiddlewareStatus,
                description="Get the status of a middleware instance.",
                inputSchema=schema.MiddlewareNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.BackupMiddleware,
                description="Backup a middleware instance.",
                inputSchema=schema.MiddlewareNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.ListMiddlewareInstanceNodes,
                description="List all nodes of a middleware instance.",
                inputSchema=schema.MiddlewareNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.RemoveMiddlewareInstanceNodes,
                description="Remove nodes from a middleware instance.",
                inputSchema=schema.RemoveMiddlewareInstanceNodesSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.ListMiddlewareInstanceChangeEvents,
                description="List all change events of a middleware instance.",
                inputSchema=schema.MiddlewareNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.ListMiddlewareInstanceAlertRules,
                description="List all alert rules of a middleware instance.",
                inputSchema=schema.MiddlewareNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.ListMiddlewareInstanceSupportLogTypes,
                description="List all support log types of a middleware instance.",
                inputSchema=schema.MiddlewareTypeNameSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.ListMiddlewareInstanceLogs,
                description="List logs of a middleware instance.",
                inputSchema=schema.MiddlewareLogSchema.model_json_schema(),
            ),
            # redis
            Tool(
                name=MegaCloudTools.CreateSingleRedisMiddleware,
                description=f"Create a single redis instance.",
                inputSchema=schema.CreateSingleRedisMiddlewareSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.CreateRedisClusterMiddleware,
                description="Create a redis cluster middleware instance.",
                inputSchema=schema.CreateRedisClusterSchema.model_json_schema(),
            ),
            Tool(
                name=MegaCloudTools.AddRedisNodes,
                description="Add nodes to a redis middleware instance.",
                inputSchema=schema.AddRedisNodeSchema.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[TextContent]:
        logger.info(f"Call tool: {name}, arguments: {arguments}")
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

            case MegaCloudTools.RestartMiddleware:
                resp = await change_middleware_state(arguments, apis.MiddlewareOperations.RESTART.value)
                return utils.to_textcontent(resp)

            case MegaCloudTools.StopMiddleware:
                resp = await change_middleware_state(arguments, apis.MiddlewareOperations.STOP.value)
                return utils.to_textcontent(resp)

            case MegaCloudTools.StartMiddleware:
                resp = await change_middleware_state(arguments, apis.MiddlewareOperations.START.value)
                return utils.to_textcontent(resp)

            case MegaCloudTools.DeleteMiddleware:
                arg = schema.MiddlewareNameSchema(**arguments)
                resp = await middleware.delete_middleware_instance(arg.middleware_instance_name)
                return utils.to_textcontent(resp)

            case MegaCloudTools.GetMiddlewareInfo:
                arg = schema.MiddlewareNameSchema(**arguments)
                resp = await middleware.get_middleware_instance_info(arg.middleware_instance_name)
                return utils.to_textcontent(resp)

            case MegaCloudTools.GetMiddlewareStatus:
                arg = schema.MiddlewareNameSchema(**arguments)
                resp = await middleware.get_middleware_instance_status(arg.middleware_instance_name)
                return utils.to_textcontent(resp)

            case MegaCloudTools.BackupMiddleware:
                arg = schema.MiddlewareNameSchema(**arguments)
                resp = await middleware.backup_middleware_instance(arg.middleware_instance_name)
                return utils.to_textcontent(resp)

            case MegaCloudTools.ListMiddlewareInstanceNodes:
                arg = schema.MiddlewareNameSchema(**arguments)
                resp = await middleware.list_middleware_instance_nodes(arg.middleware_instance_name)
                return utils.to_textcontent(resp)

            case MegaCloudTools.RemoveMiddlewareInstanceNodes:
                arg = schema.RemoveMiddlewareInstanceNodesSchema(**arguments)
                resp = await middleware.remove_middleware_instance_nodes(arg.name, arg.node_names)
                return utils.to_textcontent(resp)

            case MegaCloudTools.ListMiddlewareInstanceChangeEvents:
                arg = schema.MiddlewareNameSchema(**arguments)
                resp = await middleware.get_middleware_instance_change_events(arg.middleware_instance_name)
                return utils.to_textcontent(resp)

            case MegaCloudTools.ListMiddlewareInstanceAlertRules:
                arg = schema.MiddlewareNameSchema(**arguments)
                resp = await middleware.get_middleware_instance_alert_rules(arg.middleware_instance_name)
                return utils.to_textcontent(resp)

            case MegaCloudTools.ListMiddlewareInstanceSupportLogTypes:
                arg = schema.MiddlewareTypeNameSchema(**arguments)
                resp = await apis.get_middleware_log_types(arg.middleware_type_name)
                return utils.to_textcontent(resp)

            case MegaCloudTools.ListMiddlewareInstanceLogs:
                arg = schema.MiddlewareLogSchema(**arguments)
                resp = await middleware.get_middleware_instance_logs(arg)
                return utils.to_textcontent(resp)

            # redis
            case MegaCloudTools.CreateSingleRedisMiddleware:
                arg = schema.CreateSingleRedisMiddlewareSchema(**arguments)
                resp = await middleware.create_single_node_redis(arg)
                return utils.to_textcontent(resp)

            case MegaCloudTools.CreateRedisClusterMiddleware:
                arg = schema.CreateRedisClusterSchema(**arguments)
                resp = await middleware.create_cluster_redis(arg)
                return utils.to_textcontent(resp)

            case MegaCloudTools.AddRedisNodes:
                arg = schema.AddRedisNodeSchema(**arguments)
                resp = await middleware.add_redis_nodes(arg)
                return utils.to_textcontent(resp)

            case _:
                raise ValueError(f"Unknown tool name: {name}")

    return server


def run():
    async def _run():
        server = await serve()
        options = server.create_initialization_options()
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, options, raise_exceptions=True)

    asyncio.run(_run())
