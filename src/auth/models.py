from sqlmodel import Field, SQLModel, Relationship, UniqueConstraint
from typing import Optional, List


class AuthUser(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("login"),)
    id:  Optional[int] = Field(default=None, primary_key=True)
    login: str
    password:  str
    tokens: List["Token"] = Relationship(back_populates="user")


class Token(SQLModel, table=True):
    id:  Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="authuser.id")
    user: AuthUser = Relationship(back_populates="tokens")
    user_token: str