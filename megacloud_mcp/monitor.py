from typing import Any, Dict, List, Type
from megacloud_mcp import apis


async def get_monitor_data_of_host_load(tenant_id: int, host: str, start: int, end: int) -> List[Dict]:
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [
            {"name": "serverinfo-system-load1-avg-metric"},
            {"name": "serverinfo-system-load5-avg-metric"},
            {"name": "serverinfo-system-load15-avg-metric"},
        ],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_net_err_out(tenant_id: int, host: str, start: int, end: int) -> Dict:
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [{"name": "serverinfo-net-err-out-ratio-metric"}],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_net_err_in(tenant_id: int, host: str, start: int, end: int) -> Dict:
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [{"name": "serverinfo-net-err-in-ratio-metric"}],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_disk(tenant_id: int, host: str, start: int, end: int) -> Dict:
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [
            {"name": "serverinfo-disk-total-metric", "functions": [{"kind": "max"}], "groups": [{"by": "path.keyword"}]},
            {"name": "serverinfo-disk-used-metric", "functions": [{"kind": "max"}], "groups": [{"by": "path.keyword"}]},
        ],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_disk_input_output(tenant_id: int, host: str, start: int, end: int):
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [{"name": "serverinfo-diskio-read-bytes-ratio-metric"}, {"name": "serverinfo-diskio-write-bytes-ratio-metric"}],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_net_bytes_sent(tenant_id: int, host: str, start: int, end: int):
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [{"name": "serverinfo-net-bytes-sent-ratio-metric"}],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_net_bytes_recv(tenant_id: int, host: str, start: int, end: int):
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [{"name": "serverinfo-net-bytes-recv-ratio-metric"}],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_memory(tenant_id: int, host: str, start: int, end: int):
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [
            {"name": "serverinfo-mem-used-avg-metric"},
            {"name": "serverinfo-mem-buffered-avg-metric"},
            {"name": "serverinfo-mem-cached-avg-metric"},
            {"name": "serverinfo-mem-free-avg-metric"},
        ],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_cpu(tenant_id: int, host: str, start: int, end: int):
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [
            {"name": "serverinfo-cpu-usage-system-avg-metric"},
            {"name": "serverinfo-cpu-usage-user-avg-metric"},
            {"name": "serverinfo-cpu-usage-iowait-avg-metric"},
            {"name": "serverinfo-cpu-usage-idle-avg-metric"},
        ],
    }
    return await apis.get_monitor_data(tenant_id, d)


class MiddlewareMonitorInterface:
    @classmethod
    def get_monitor_type(cls) -> list[str]:
        raise NotImplementedError("get_monitor_type() must be implemented in subclasses")

    @classmethod
    def get_monitor_metrics(cls, monitor_type: str) -> Any:
        raise NotImplementedError("get_monitor_metrics() must be implemented in subclasses")


class PrometheusMonitor(MiddlewareMonitorInterface):
    monitor_types = ["SamplesAppended"]
    monitor_metrics = {"SamplesAppended": [{"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-tsdb-head-samples-appended-total-metric"}]}

    @classmethod
    def get_monitor_type(cls) -> list[str]:
        return cls.monitor_types


MIDDLEWARE_MONITOR_MAP: Dict[str, Type[MiddlewareMonitorInterface]] = {
    "prometheus": PrometheusMonitor,
}


async def get_middleware_monitor_metrics(middleware_instance_name: str) -> List[str]:
    instance = await apis.get_middleware_instance(middleware_instance_name)
    middleware_name = instance.middleware_name.lower()
    if middleware_name not in MIDDLEWARE_MONITOR_MAP:
        raise ValueError(f"Middleware {middleware_name} is not supported")
    middleware_monitor = MIDDLEWARE_MONITOR_MAP[middleware_name]
    return middleware_monitor.get_monitor_type()
