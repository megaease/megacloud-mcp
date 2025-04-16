import dataclasses
from . import apis
from . import utils


REDIS_NAME = "Redis"
REDIS_TYPE = 4


async def create_single_redis(host_name: str):
    # create a new redis node
    create_node_req = apis.create_single_node_request(REDIS_TYPE)
    nodes = await apis.create_nodes(create_node_req)
    node = nodes[0]

    # find target host
    hosts = await apis.list_available_hosts()
    host = list(filter(lambda x: x.host_name == host_name, hosts))
    if len(host) == 0:
        raise Exception(f"Host {host_name} not found")
    host = host[0]

    middleware_node = apis.MiddlewareNode(
        node_name=node.node_name,
        middleware_type=REDIS_TYPE,
        group_tags=node.group_tags,
        tenant_id=node.tenant_id,
        host_id=host.host_id,
        host_name=host.host_name,
        os_arch=host.os_arch,
    )
    middleware_node = dataclasses.asdict(middleware_node)

    name = utils.generate_name(REDIS_NAME.lower())
    config = apis.CreateMiddlewareInstanceConfig(
        middlewareName=REDIS_NAME,
        middleware_type=REDIS_TYPE,
        name=name,
        nodes=[middleware_node],
        configs={"maxmemory": 4294967296},
        major_version="7.4",
        minor_version="7.4.2",
    )
    request = apis.create_middleware_instance_request(config)
    response = await apis.create_middleware_instance(request)
    return response
