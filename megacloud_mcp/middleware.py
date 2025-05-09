from typing import Dict, List, Optional
from pydantic import BaseModel
import time

from megacloud_mcp import apis
from megacloud_mcp import utils
from megacloud_mcp import schema

REDIS_NAME = "Redis"


class CreateSingleNodeMiddlewareRequest(BaseModel):
    middleware_name: str
    host_name: str
    configs: dict
    major_version: str
    minor_version: str
    name: Optional[str] = None


async def create_single_node_middleware(req: CreateSingleNodeMiddlewareRequest):
    middleware_type = await apis.get_middleware_type(req.middleware_name)
    create_nodes_req = apis.create_nodes_request(middleware_type, {"master": 1})

    nodes = await apis.create_nodes(create_nodes_req)
    node = nodes[0]

    # find target host
    hosts = await apis.list_available_hosts()
    host = list(filter(lambda x: x.host_name == req.host_name, hosts))
    if len(host) == 0:
        raise Exception(f"Host {req.host_name} not found")
    host = host[0]

    middleware_node = apis.MiddlewareNode(
        node_name=node.node_name,
        middleware_type=middleware_type,
        group_tags=node.group_tags,
        tenant_id=node.tenant_id,
        host_id=str(host.host_id),
        host_name=host.host_name,
        os_arch=host.os_arch,
    )
    middleware_node = middleware_node.model_dump()

    name = req.name if req.name else utils.generate_name(req.middleware_name.lower())
    config = apis.CreateMiddlewareInstanceConfig(
        middlewareName=req.middleware_name,
        middleware_type=middleware_type,
        name=name,
        nodes=[middleware_node],
        configs=req.configs,
        major_version=req.major_version,
        minor_version=req.minor_version,
        group_configs=[
            {"group": "master", "configs": {}},
        ],
    )
    request = apis.create_middleware_instance_request(config)
    response = await apis.create_middleware_instance(request)
    return response


async def create_single_node_redis(req: schema.CreateSingleRedisMiddlewareSchema):
    r = CreateSingleNodeMiddlewareRequest(
        name=req.name,
        middleware_name=REDIS_NAME,
        host_name=req.host_name,
        configs={"maxmemory": req.max_memory_in_gb * 1024 * 1024 * 1024},
        major_version="7.4",
        minor_version="7.4.2",
    )
    response = await create_single_node_middleware(r)
    return response


class CreateClusterMiddlewareRequest(BaseModel):
    name: Optional[str] = None
    middleware_name: str
    hosts: dict[str, List[str]]
    configs: dict
    major_version: str
    minor_version: str


async def create_cluster_middleware(req: CreateClusterMiddlewareRequest):
    middleware_type = await apis.get_middleware_type(req.middleware_name)

    # create nodes
    node_count: Dict[str, int] = {}
    for group, host_names in req.hosts.items():
        node_count[group] = len(host_names)
    create_nodes_req = apis.create_nodes_request(middleware_type, node_count)
    nodes = await apis.create_nodes(create_nodes_req)
    node_map: Dict[str, List[apis.Node]] = {}
    for node in nodes:
        group = node.group_tags
        if group not in node_map:
            node_map[group] = []
        node_map[group].append(node)

    # find target host
    hosts = await apis.list_available_hosts()
    host_map: Dict[str, apis.Host] = {}
    for host in hosts:
        host_map[host.host_name] = host

    # create middleware nodes
    middleware_nodes: List[apis.MiddlewareNode] = []
    for group, nodes in node_map.items():
        for i, node in enumerate(nodes):
            host_name = req.hosts[group][i]
            host = host_map.get(host_name)
            if not host:
                raise Exception(f"Host {host_name} not found")
            middleware_node = apis.MiddlewareNode(
                node_name=node.node_name,
                middleware_type=middleware_type,
                group_tags=node.group_tags,
                tenant_id=node.tenant_id,
                host_id=str(host.host_id),
                host_name=host.host_name,
                os_arch=host.os_arch,
            )
            middleware_nodes.append(middleware_node)
    req_nodes = [node.model_dump() for node in middleware_nodes]

    # create middleware instances
    name = req.name if req.name else utils.generate_name(req.middleware_name.lower())
    group_configs = list(map(lambda group: {"group": group, "configs": {}}, req.hosts.keys()))
    config = apis.CreateMiddlewareInstanceConfig(
        middlewareName=req.middleware_name,
        middleware_type=middleware_type,
        name=name,
        nodes=req_nodes,
        configs=req.configs,
        major_version=req.major_version,
        minor_version=req.minor_version,
        group_configs=group_configs,
    )
    request = apis.create_middleware_instance_request(config)
    response = await apis.create_middleware_instance(request)
    return response


async def create_cluster_redis(req: schema.CreateRedisClusterSchema):
    r = CreateClusterMiddlewareRequest(
        name=req.name,
        middleware_name=REDIS_NAME,
        hosts={"master": req.master_host_names, "replica": req.replica_host_names},
        configs={"maxmemory": req.max_memory_in_gb * 1024 * 1024 * 1024},
        major_version="7.4",
        minor_version="7.4.2",
    )
    response = await create_cluster_middleware(r)
    return response


async def change_middleware_state(name: str, operation: int):
    middleware_instances = await apis.list_current_middleware_instances()
    instance = list(
        filter(
            lambda x: x.name == name,
            middleware_instances,
        )
    )
    available_names = [instance.name for instance in middleware_instances]
    if len(instance) == 0:
        raise Exception(f"Middleware instance {name} not found, available names: {available_names}")
    instance = instance[0]
    resp = await apis.put_middleware_instance(instance.instance_id, operation)
    return resp


async def delete_middleware_instance(name: str):
    id = await apis.get_middleware_instance_id(name)
    resp = await apis.del_middleware_instance(id)
    return resp


async def get_middleware_instance_info(name: str):
    id = await apis.get_middleware_instance_id(name)
    resp = await apis.get_middleware_instance_info(id)
    return resp


async def get_middleware_instance_status(name: str):
    id = await apis.get_middleware_instance_id(name)
    resp = await apis.get_middleware_instance_status(id)
    return resp


async def backup_middleware_instance(name: str):
    id = await apis.get_middleware_instance_id(name)
    resp = await apis.backup_middleware_instance(id)
    return resp


async def add_middleware_nodes(name: str, middleware_type: int, node_config: dict[str, List[str]]):
    # create nodes
    node_count: Dict[str, int] = {}
    for group, host_names in node_config.items():
        node_count[group] = len(host_names)
    create_nodes_req = apis.create_nodes_request(middleware_type, node_count)
    nodes = await apis.create_nodes(create_nodes_req)

    # node map
    node_map: Dict[str, List[apis.Node]] = {}
    for node in nodes:
        group = node.group_tags
        if group not in node_map:
            node_map[group] = []
        node_map[group].append(node)

    # create host map
    hosts = await apis.list_available_hosts()
    host_map: Dict[str, apis.Host] = {}
    for host in hosts:
        host_map[host.host_name] = host

    # create middleware nodes
    middleware_nodes: List[apis.MiddlewareNode] = []
    for group, nodes in node_map.items():
        for i, node in enumerate(nodes):
            host_name = node_config[group][i]
            host = host_map.get(host_name)
            if not host:
                raise Exception(f"Host {host_name} not found")
            middleware_node = apis.MiddlewareNode(
                node_name=node.node_name,
                middleware_type=middleware_type,
                group_tags=node.group_tags,
                tenant_id=node.tenant_id,
                host_id=str(host.host_id),
                host_name=host.host_name,
                os_arch=host.os_arch,
            )
            middleware_nodes.append(middleware_node)

    # do add node
    id = await apis.get_middleware_instance_id(name)
    add_node_req = apis.AddMiddlewareInstanceNodesRequest(
        nodes=middleware_nodes,
        node_configs=[],
        group_configs=[],
    )
    resp = await apis.add_middleware_instance_nodes(id, add_node_req)
    return resp


async def add_redis_nodes(req: schema.AddRedisNodeSchema):
    # check req validity
    if req.master_host_names is None and req.replica_host_names is None:
        raise Exception("At least one of master_host_names or replica_host_names must be provided")
    master_host_names = req.master_host_names if req.master_host_names else []
    replica_host_names = req.replica_host_names if req.replica_host_names else []
    if len(master_host_names) + len(replica_host_names) == 0:
        raise Exception("At least one of master_host_names or replica_host_names must be provided")

    # prepare node config
    node_config: Dict[str, List[str]] = {}
    if len(master_host_names) > 0:
        node_config["master"] = master_host_names
    if len(replica_host_names) > 0:
        node_config["replica"] = replica_host_names

    middleware_type = await apis.get_middleware_type(REDIS_NAME)
    resp = await add_middleware_nodes(req.name, middleware_type, node_config)
    return resp


async def list_middleware_instance_nodes(name: str) -> List[apis.MiddlewareNodeInfo]:
    id = await apis.get_middleware_instance_id(name)
    return await apis.list_middleware_instance_nodes(id)


async def remove_middleware_instance_nodes(name: str, node_names: List[str]):
    id = await apis.get_middleware_instance_id(name)

    nodes = await apis.list_middleware_instance_nodes(id)
    node_ids = []
    for n in nodes:
        if n.node_name in node_names:
            node_ids.append(n.id)
    if len(node_ids) != len(node_names):
        raise Exception(f"Node names {node_names} not found in instance {name}")

    resp = await apis.remove_middleware_instance_nodes(id, node_ids)
    return resp


async def get_middleware_instance_change_events(name: str):
    instance = await apis.get_middleware_instance(name)
    result = await apis.get_middleware_instance_change_events(instance.middleware_type, instance.instance_id)
    return result


async def get_middleware_instance_alert_rules(name: str):
    result = await apis.get_middleware_instance_alert_rules(name)
    return result


async def get_middleware_instance_logs(arg: schema.MiddlewareLogSchema):
    start_time, end_time = utils.get_start_end_time(arg.time_interval_in_minutes)
    result = await apis.get_middleware_instance_log(arg.middleware_instance_name, start_time, end_time, arg.log_type, arg.current_page)
    return result


async def get_monitor_data_of_host_load(arg: schema.HostNameTimeIntervalSchema):
    tenant_id = await apis.get_tenant_id()
    start_time, end_time = utils.get_start_end_time(arg.time_interval_in_minutes)
    result = await apis.get_monitor_data_of_host_load(tenant_id, arg.host_name, start_time, end_time)
    return result


async def get_monitor_data_of_host_net_err_out(arg: schema.HostNameTimeIntervalSchema):
    tenant_id = await apis.get_tenant_id()
    start_time, end_time = utils.get_start_end_time(arg.time_interval_in_minutes)
    result = await apis.get_monitor_data_of_host_net_err_out(tenant_id, arg.host_name, start_time, end_time)
    return result


async def get_monitor_data_of_host_net_err_in(arg: schema.HostNameTimeIntervalSchema):
    tenant_id = await apis.get_tenant_id()
    start_time, end_time = utils.get_start_end_time(arg.time_interval_in_minutes)
    result = await apis.get_monitor_data_of_host_net_err_in(tenant_id, arg.host_name, start_time, end_time)
    return result


async def get_monitor_data_of_host_disk(arg: schema.HostNameTimeIntervalSchema):
    tenant_id = await apis.get_tenant_id()
    start_time, end_time = utils.get_start_end_time(arg.time_interval_in_minutes)
    result = await apis.get_monitor_data_of_host_disk(tenant_id, arg.host_name, start_time, end_time)
    return result


async def get_monitor_data_of_host_disk_input_output(arg: schema.HostNameTimeIntervalSchema):
    tenant_id = await apis.get_tenant_id()
    start_time, end_time = utils.get_start_end_time(arg.time_interval_in_minutes)
    result = await apis.get_monitor_data_of_host_disk_input_output(tenant_id, arg.host_name, start_time, end_time)
    return result
