from pydantic import BaseModel


class CountSchema(BaseModel):
    dt: str
    count: int