from typing import Optional
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


class MiddlewareNameSchema(BaseModel):
    middleware_instance_name: str
