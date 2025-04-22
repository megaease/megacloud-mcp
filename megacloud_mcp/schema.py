from typing import Optional
from pydantic import BaseModel


class EmptySchema(BaseModel):
    pass


class CreateSingleRedisMiddlewareSchema(BaseModel):
    host_name: str
    name: Optional[str] = None


class CreateRedisClusterSchema(BaseModel):
    name: Optional[str] = None
    master_host_names: list[str]
    replica_host_names: list[str]


class ChangeMiddlewareStatusSchema(BaseModel):
    middleware_instance_name: str
