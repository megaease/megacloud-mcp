import dataclasses
from typing import List

from .settings import BACKEND_URL
from .client import async_client


@dataclasses.dataclass
class Node:
    node_name: str
    middleware_type: int
    group_tags: str
    tenant_id: int


def create_single_node_request(middleware_type: int) -> dict:
    return {
        "middleware_type": middleware_type,
        "group_infos": [
            {"group": "master", "group_num": 1, "node_num": 1, "is_shard": False}
        ],
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


@dataclasses.dataclass
class MiddlewareNode:
    node_name: str
    middleware_type: int
    group_tags: str
    tenant_id: int
    host_id: str
    host_name: str
    os_arch: str


@dataclasses.dataclass
class CreateMiddlewareInstanceConfig:
    middlewareName: str
    middleware_type: int
    name: str
    nodes: List[dict]
    configs: dict
    major_version: str
    minor_version: str


def create_middleware_instance_request(
    config: CreateMiddlewareInstanceConfig,
) -> dict:
    request = {
        "middlewareName": config.middlewareName,
        "middleware_type": config.middleware_type,
        "tag_ids": [],
        "name": config.name,
        "deploy_mode": "0",
        "nodes": config.nodes,
        "general_config": {
            "data_dir": f"/data/megaease/redis/{config.name}",
            "backup_dir": f"/backup/megaease/redis/{config.name}",
            "log_dir": f"/var/log/megaease/redis/{config.name}",
        },
        "configs": config.configs,
        "group_configs": [{"group": "master", "configs": {}}],
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


@dataclasses.dataclass
class Host:
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
