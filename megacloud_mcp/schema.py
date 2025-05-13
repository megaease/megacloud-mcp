from typing import Literal, Optional
from pydantic import BaseModel


class EmptySchema(BaseModel):
    pass


class CreateSingleRedisMiddlewareSchema(BaseModel):
    host_name: str
    max_memory_in_gb: int = 4
    name: Optional[str] = None


class CreateRedisClusterSchema(BaseModel):
    name: Optional[str] = None
    max_memory_in_gb: int = 4
    master_host_names: list[str]
    replica_host_names: list[str]


class AddRedisNodeSchema(BaseModel):
    name: str
    master_host_names: Optional[list[str]] = None
    replica_host_names: Optional[list[str]] = None


class RemoveMiddlewareInstanceNodesSchema(BaseModel):
    name: str
    node_names: list[str]


class MiddlewareNameSchema(BaseModel):
    middleware_instance_name: str


class MiddlewareTypeNameSchema(BaseModel):
    middleware_type_name: str


class MiddlewareLogSchema(BaseModel):
    middleware_instance_name: str
    log_type: str
    time_interval_in_minutes: int = 30
    current_page: int = 1


class HostNameTimeIntervalSchema(BaseModel):
    host_name: str
    time_interval_in_minutes: int = 60


class CreateAlertRuleSchema(BaseModel):
    name: str
    description: str
    resolved_description: str
    middleware_instance_name: str
    level: Literal["CLEAR", "INDETERMINATE", "CRITICAL", "MAJOR", "MINOR", "WARNING"]
    alert_metric_happen_times: int = 1
    alert_metric_happen_duration_in_seconds: int = 60
    alert_metric_type: str
    alert_metric_operator: Literal["eq", "neq", "lt", "lte", "gt", "gte"]
    alert_metric_value: int


class MiddlewareInstanceAlertRuleNameSchema(BaseModel):
    middleware_instance_name: str
    alert_rule_name: str
