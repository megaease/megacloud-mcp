from typing import Dict, List
from pydantic import BaseModel

from . import apis
from . import utils


REDIS_NAME = "Redis"


class CreateSingleNodeMiddlewareRequest(BaseModel):
    middleware_name: str
    host_name: str
    configs: dict
    major_version: str
    minor_version: str


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

    name = utils.generate_name(req.middleware_name.lower())
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


async def create_single_node_redis(host_name: str):
    req = CreateSingleNodeMiddlewareRequest(
        middleware_name=REDIS_NAME,
        host_name=host_name,
        configs={"maxmemory": 4294967296},
        major_version="7.4",
        minor_version="7.4.2",
    )
    response = await create_single_node_middleware(req)
    return response


class CreateClusterMiddlewareRequest(BaseModel):
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
    name = utils.generate_name(req.middleware_name.lower())
    group_configs = list(
        map(lambda group: {"group": group, "configs": {}}, req.hosts.keys())
    )
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


async def create_cluster_redis(master_hosts: List[str], replica_hosts: List[str]):
    req = CreateClusterMiddlewareRequest(
        middleware_name=REDIS_NAME,
        hosts={"master": master_hosts, "replica": replica_hosts},
        configs={"maxmemory": 4294967296},
        major_version="7.4",
        minor_version="7.4.2",
    )
    response = await create_cluster_middleware(req)
    return response
