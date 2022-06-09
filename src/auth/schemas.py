from pydantic import BaseModel


class RedisMessageSchema(BaseModel):
    dt: str
    count: int
    
    
class AuthUserSchema(BaseModel):
    login: str
    password: str