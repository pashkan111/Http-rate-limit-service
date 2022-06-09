from pydantic import BaseModel


class RedisMessageSchema(BaseModel):
    dt: str
    count: int