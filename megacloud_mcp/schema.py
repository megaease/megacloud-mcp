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


class AddRedisNodeSchema(BaseModel):
    name: str
    master_host_names: Optional[list[str]] = None
    replica_host_names: Optional[list[str]] = None


class MiddlewareNameSchema(BaseModel):
    middleware_instance_name: str
