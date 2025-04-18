from pydantic import BaseModel


SUPPORTED_MIDDLEWARES = [
    "Redis",
]


class CreateSingleNodeMiddlewareSchema(BaseModel):
    middleware_type_name: str
    host_name: str


class CreateRedisClusterSchema(BaseModel):
    master_host_names: list[str]
    replica_host_names: list[str]


class ChangeMiddlewareStatusSchema(BaseModel):
    middleware_instance_name: str
