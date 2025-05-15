from enum import Enum
from typing import Any, Dict, List
from pydantic import BaseModel

from megacloud_mcp.settings import BACKEND_URL
from megacloud_mcp.client import async_client
from megacloud_mcp.log import logger
from megacloud_mcp.utils import from_unix_mill_to_datetime


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
        logger.error(f"Failed to create nodes: {body}")
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
        logger.error(f"Failed to create middleware instance, body: {body}")
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


_MIDDLEWARE_TYPE2NAME: Dict[int, str] = {}
_MIDDLEWARE_NAME2TYPE: Dict[str, int] = {}


async def get_middleware_name(middleware_type: int) -> str:
    if len(_MIDDLEWARE_TYPE2NAME) == 0:
        middleware_types = await list_available_middleware_type()
        for middleware in middleware_types:
            _MIDDLEWARE_TYPE2NAME[middleware.middleware_type] = middleware.name
    return _MIDDLEWARE_TYPE2NAME.get(middleware_type, "Unknown")


async def get_middleware_type(middleware_name: str) -> int:
    if len(_MIDDLEWARE_NAME2TYPE) == 0:
        middleware_types = await list_available_middleware_type()
        for middleware in middleware_types:
            _MIDDLEWARE_NAME2TYPE[middleware.name.lower()] = middleware.middleware_type
    return _MIDDLEWARE_NAME2TYPE.get(middleware_name.lower(), -1)


class MiddlewareInstance(BaseModel):
    instance_id: int
    name: str
    middleware_type: int
    middleware_name: str
    major_version: str
    minor_version: str
    status: dict


async def list_current_middleware_instances() -> List[MiddlewareInstance]:
    url = BACKEND_URL + "/v1/middleware/management/instance?name=&hostName=&rows=100&page=1&group=middleware"
    response = await async_client.get(url)
    result = []
    if response.status_code == 200:
        data = response.json()
        for instance in data["list"]:
            instance["middleware_name"] = await get_middleware_name(instance["middleware_type"])
            result.append(MiddlewareInstance(**instance))
        return result
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class MiddlewareOperations(Enum):
    RESTART = 5
    STOP = 4
    START = 2


async def put_middleware_instance(id: int, operation: int):
    url = BACKEND_URL + f"/v1/middleware/management/instance/{id}/operations/{operation}"
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


async def get_middleware_instance_info(id: int) -> dict:
    url = BACKEND_URL + f"/v1/middleware/management/instance/{id}"
    response = await async_client.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


async def get_middleware_instance_status(id: int) -> dict:
    url = BACKEND_URL + f"/v1/middleware/management/instance/{id}/status"
    response = await async_client.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


async def get_middleware_instance(name: str) -> MiddlewareInstance:
    middleware_instances = await list_current_middleware_instances()
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
    return instance


async def get_middleware_instance_id(name: str) -> int:
    instance = await get_middleware_instance(name)
    return instance.instance_id


async def backup_middleware_instance(id: int):
    url = BACKEND_URL + f"/v1/middleware/management/backup/{id}/backup-immediately"
    response = await async_client.post(url)
    if response.status_code == 200:
        return "OK"
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class AddMiddlewareInstanceNodesRequest(BaseModel):
    nodes: List[MiddlewareNode]
    node_configs: List[dict]
    group_configs: List[dict]


async def add_middleware_instance_nodes(id: int, req: AddMiddlewareInstanceNodesRequest):
    url = BACKEND_URL + f"/v1/middleware/management/instance/{id}/add-nodes"
    response = await async_client.post(url, json=req.model_dump())
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class MiddlewareNodeInfo(BaseModel):
    id: int
    instance_id: int
    host_id: int
    host_ip: str
    host_name: str
    status: dict
    middleware_type: int
    group_tags: str
    node_name: str
    cpu: int
    memory: int
    storage: int
    node_containers: List[dict]


async def list_middleware_instance_nodes(id: int) -> List[MiddlewareNodeInfo]:
    url = BACKEND_URL + f"/v1/middleware/management/instance/{id}/nodes"
    response = await async_client.get(url)
    if response.status_code == 200:
        data = response.json()
        nodes = [MiddlewareNodeInfo(**node) for node in data]
        return nodes
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


async def remove_middleware_instance_nodes(id: int, node_ids: List[int]):
    url = BACKEND_URL + f"/v1/middleware/management/instance/{id}/remove-nodes"
    response = await async_client.post(url, json={"nodes": node_ids})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class MiddlewareInstanceChangeEvent(BaseModel):
    event: str
    result: str
    status: str
    create_time: str
    update_time: str


async def get_middleware_instance_change_events(middleware_type: int, id: int) -> List[MiddlewareInstanceChangeEvent]:
    url = BACKEND_URL + f"/v1/middleware/management/state-machine/{middleware_type}/{id}/changes?page=1&pageSize=20"
    response = await async_client.get(url)
    if response.status_code == 200:
        data = response.json()
        events: list = data["list"]
        result = []
        for event in events:
            event_val = event["event"]["desc"]
            result_val = event["result"]["desc"]
            create_time = from_unix_mill_to_datetime(event["create_at"])
            update_time = from_unix_mill_to_datetime(event["update_at"])
            status = f"""from {event["from"]} to {event["to"]}"""
            result.append(
                MiddlewareInstanceChangeEvent(
                    event=event_val,
                    result=result_val,
                    status=status,
                    create_time=create_time,
                    update_time=update_time,
                )
            )
        return result
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


ALERTLEVELS = {
    "1": "CLEAR",
    "2": "INDETERMINATE",
    "3": "CRITICAL",
    "4": "MAJOR",
    "5": "MINOR",
    "6": "WARNING",
}

ALERTLEVELS_REVERSE = {v: k for k, v in ALERTLEVELS.items()}

ALERTSTATUS = {
    0: "Stopped",
    1: "Running",
}


class AlertRule(BaseModel):
    id: int
    name: str
    updated_at: str
    description: str
    resolved_description: str
    rules: str
    status: str
    level: str


async def get_middleware_instance_alert_rule_json(name: str) -> list[dict]:
    url = BACKEND_URL + f"/v1/monitor/event-rules?name=&zone=&domain=&service={name}&page_size=10"
    response = await async_client.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["data"]
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


async def get_middleware_instance_alert_rules(name: str) -> List[AlertRule]:
    data = await get_middleware_instance_alert_rule_json(name)
    rules = []
    for rule in data:
        rule["level"] = ALERTLEVELS.get(rule["level"], "Unknown")
        rule["status"] = ALERTSTATUS.get(rule["status"], "Unknown")
        rule["updated_at"] = from_unix_mill_to_datetime(rule["updated_at"])
        rules.append(AlertRule(**rule))
    return rules


RESOURCETYPEMAP = {
    1: "MySQL",
    2: "ElasticSearch",
    3: "Kibana",
    4: "Redis",
    5: "ZooKeeper",
    6: "Kafka",
    7: "MongoDB",
    8: "Kubernetes",
    9: "monitor-integration middleware",
    10: "monitor-service only",
    11: "Easegress",
    13: "Docker App",
    14: "Prometheus",
    15: "Kubernetes App",
    17: "Docker",
    18: "EaseMesh",
    19: "MinIO",
    20: "Nginx",
    21: "PostgreSQL",
    102: "Cloudflared",
}

LOGMAP: Dict[str, List[str]] = {
    "redis-log": ["main_log"],
    "elasticsearch-log": [
        "main_log",
        "slowquery_log",
        "slowindex_log",
        "gc_log",
    ],
    "mysql-log": [
        "general_log",
        "slowquery_log",
        "error_log",
    ],
    "kafka-log": ["server_log", "zookeeper_log"],
    "zookeeper-log": ["server_log"],
    "easegress-log": [
        "main_log",
        "admin_log",
        "etcd_client_log",
        "etcd_server_log",
        "filter_http_access_log",
        "filter_http_dump_log",
    ],
    "prometheus-log": ["main_log"],
    "minio-log": ["minio_server_log", "minio_audit_log"],
    "nginx-log": ["access_log", "error_log"],
    "postgresql-log": ["postgresql_log"],
}


def get_log_kind_name(middleware_type: int) -> str:
    try:
        middleware_name = RESOURCETYPEMAP[middleware_type]
        log_name = middleware_name.lower() + "-log"
        assert log_name in LOGMAP
        return log_name
    except Exception as e:
        raise Exception(f"Error: {e}, middleware_type: {middleware_type} not supported, available types: {RESOURCETYPEMAP.keys()}")


async def get_middleware_log_types(type_name: str):
    log_name = type_name.lower() + "-log"
    if log_name in LOGMAP:
        return LOGMAP[log_name]
    else:
        types = list(map(lambda x: x.removesuffix("-log"), LOGMAP.keys()))
        raise Exception(f"Error: {type_name} not supported, available types: {types}")


class MiddlewareInstanceLogs(BaseModel):
    total_size: int
    current_page: int
    page_size: int
    data: List[dict]


async def get_middleware_instance_log(name: str, start: int, end: int, log_type: str, page: int) -> MiddlewareInstanceLogs:
    instance = await get_middleware_instance(name)
    log_kind = get_log_kind_name(instance.middleware_type)
    if log_type not in LOGMAP[log_kind]:
        raise Exception(f"Error: {log_type} not supported, available types: {LOGMAP[log_kind]}")
    url = (
        BACKEND_URL
        + f"/v1/monitor/middleware-logs?start={start}&end={end}&service={name}&keyword=&hostIpv4=&current_page={page}&page_size=50&kind={log_kind}&log_type={log_type}&host_name=&node_name="
    )
    response = await async_client.get(url)
    if response.status_code == 200:
        data = response.json()
        log_data = []
        for log in data["data"]:
            log["log_time"] = from_unix_mill_to_datetime(int(log["log_time"]))
            log_data.append(log)
        logs = MiddlewareInstanceLogs(
            total_size=data["total_size"],
            current_page=data["current_page"],
            page_size=data["page_size"],
            data=log_data,
        )
        return logs
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class AuthorizationInfo(BaseModel):
    username: str
    tenant_id: int
    tenant_name: str
    privileges: list
    role: list
    role_set: list
    permissions: list
    resources: list


async def get_authorizations() -> AuthorizationInfo:
    url = BACKEND_URL + "/v1/control/my-authorizations"
    response = await async_client.get(url)
    if response.status_code == 200:
        data = response.json()
        return AuthorizationInfo(**data)
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


async def get_tenant_id() -> int:
    auth = await get_authorizations()
    return auth.tenant_id


async def get_monitor_data(tenant_id: int, data: dict) -> Any:
    url = BACKEND_URL + f"/v1/monitor/tenants/{tenant_id}/time-series"
    response = await async_client.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class MiddlewareAlertMetric(BaseModel):
    name: str
    desc: str


async def get_middleware_alert_metrics(middleware_type_name: str) -> List[Dict]:
    url = BACKEND_URL + f"/v1/monitor/dashboard-metric-trees?metric_type=origin&groups={middleware_type_name}"
    response = await async_client.get(url)
    if response.status_code == 200:
        data = response.json()
        metrics = []
        for m in data["root"][0]["children"][0]["children"][0]["children"]:
            mm = MiddlewareAlertMetric(**m)
            metrics.append(mm)
        return metrics
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


class MiddlewareAlertRuleReq(BaseModel):
    name: str
    description: str
    resolved_description: str
    type: str = "0"
    service: str
    status: int = 0
    schedule: str
    level: str
    rules: str


async def make_alert_rule_schedule():
    return [
        {
            "period_unit": "weekly",
            "start_in_sec": "",
            "end_in_sec": "",
            "days": [],
        }
    ]


def make_alert_rule_rule(count: int, duration: int, value: int, op: str, metric: str) -> dict:
    return {
        "type": "builder",
        "count": count,
        "duration": duration,
        "predicate": {"value": value, "op": op},
        "metric": metric,
        "extensions": [],
    }


async def create_middleware_alert_rule(req: MiddlewareAlertRuleReq):
    url = BACKEND_URL + "/v1/monitor/event-rules"
    response = await async_client.post(url, json=req.model_dump())
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


async def put_middleware_alert_rule(id: int, body: dict):
    url = BACKEND_URL + f"/v1/monitor/event-rules/{id}"
    response = await async_client.put(url, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


async def delete_middleware_alert_rule(id: int):
    url = BACKEND_URL + f"/v1/monitor/event-rules/{id}"
    response = await async_client.delete(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")
