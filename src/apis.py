from enum import Enum
from typing import Dict, List
from pydantic import BaseModel

from .settings import BACKEND_URL
from .client import async_client


class Node(BaseModel):
    node_name: str
    middleware_type: int
    group_tags: str
    tenant_id: int


def create_nodes_request(middleware_type: int, map: Dict[str, int]) -> dict:
    group_infos = []
    for group, node_num in map.items():
        group_info = {
            "group": group,
            "group_num": 1,
            "node_num": node_num,
            "is_shard": False,
        }
        group_infos.append(group_info)

    return {
        "middleware_type": middleware_type,
        "group_infos": group_infos,
    }


async def create_nodes(body: dict) -> List[Node]:
    url = BACKEND_URL + "/v1/middleware/management/instance/nodes"
    response = await async_client.post(url, json=body)
    if response.status_code == 200:
        json_data = response.json()
        nodes = [Node(**node) for node in json_data]
        return nodes
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class MiddlewareNode(BaseModel):
    node_name: str
    middleware_type: int
    group_tags: str
    tenant_id: int
    host_id: str
    host_name: str
    os_arch: str


class CreateMiddlewareInstanceConfig(BaseModel):
    middlewareName: str
    middleware_type: int
    name: str
    nodes: List[dict]
    configs: dict
    major_version: str
    minor_version: str
    group_configs: List[dict]


def create_middleware_instance_request(
    config: CreateMiddlewareInstanceConfig,
) -> dict:
    path = f"{config.middlewareName.lower()}/{config.name}"

    request = {
        "middlewareName": config.middlewareName,
        "middleware_type": config.middleware_type,
        "tag_ids": [],
        "name": config.name,
        "deploy_mode": "0" if len(config.nodes) == 1 else "1",
        "nodes": config.nodes,
        "general_config": {
            "data_dir": f"/data/megaease/{path}",
            "backup_dir": f"/backup/megaease/{path}",
            "log_dir": f"/var/log/megaease/{path}",
        },
        "configs": config.configs,
        "group_configs": config.group_configs,
        "node_configs": [],
        "major_version": config.major_version,
        "minor_version": config.minor_version,
        "auto_deploy": 0,
        "app_images": [],
    }
    return request


async def create_middleware_instance(body: dict):
    url = BACKEND_URL + "/v1/middleware/management/instance"
    response = await async_client.post(url, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class Host(BaseModel):
    host_id: int
    host_name: str
    ip_addr: str
    status: dict
    os_version: str
    os_arch: str
    host_os: str
    host_arch: str


async def list_available_hosts() -> List[Host]:
    url = BACKEND_URL + "/v1/middleware/management/hosts/get-for-deploy"
    response = await async_client.get(url)
    if response.status_code == 200:
        data = response.json()
        hosts = [Host(**host) for host in data]
        return hosts
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class MiddlewareType(BaseModel):
    name: str
    middleware_type: int


async def list_available_middleware_type() -> List[MiddlewareType]:
    url = BACKEND_URL + "/v1/middleware/management/services?pageSize=50"
    response = await async_client.get(url)
    if response.status_code == 200:
        data = response.json()
        types = [MiddlewareType(**type) for type in data["list"]]
        return types
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


MIDDLEWARE_TYPE2NAME: Dict[int, str] = {}
MIDDLEWARE_NAME2TYPE: Dict[str, int] = {}


async def get_middleware_name(middleware_type: int) -> str:
    if len(MIDDLEWARE_TYPE2NAME) == 0:
        middleware_types = await list_available_middleware_type()
        for middleware in middleware_types:
            MIDDLEWARE_TYPE2NAME[middleware.middleware_type] = middleware.name
    return MIDDLEWARE_TYPE2NAME.get(middleware_type, "Unknown")


async def get_middleware_type(middleware_name: str) -> int:
    if len(MIDDLEWARE_NAME2TYPE) == 0:
        middleware_types = await list_available_middleware_type()
        for middleware in middleware_types:
            MIDDLEWARE_NAME2TYPE[middleware.name.lower()] = middleware.middleware_type
    return MIDDLEWARE_NAME2TYPE.get(middleware_name.lower(), -1)


class MiddlewareInstance(BaseModel):
    instance_id: int
    name: str
    middleware_type: int
    middleware_name: str
    major_version: str
    minor_version: str
    status: dict


async def list_current_middleware_instances() -> List[MiddlewareInstance]:
    url = (
        BACKEND_URL
        + "/v1/middleware/management/instance?name=&hostName=&rows=100&page=1&group=middleware"
    )
    response = await async_client.get(url)
    result = []
    if response.status_code == 200:
        data = response.json()
        for instance in data["list"]:
            instance["middleware_name"] = get_middleware_name(
                instance["middleware_type"]
            )
            result.append(MiddlewareInstance(**instance))
        return result
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class MiddlewareOperations(Enum):
    RESTART = 5
    STOP = 4
    START = 2


async def put_middleware_instance(id: int, operation: int):
    url = (
        BACKEND_URL + f"/v1/middleware/management/instance/{id}/operations/{operation}"
    )
    response = await async_client.put(url)
    if response.status_code == 200:
        return "OK"
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


async def del_middleware_instance(id: int):
    url = BACKEND_URL + f"/v1/middleware/management/instance/{id}"
    response = await async_client.delete(url)
    if response.status_code == 200:
        return "OK"
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")
