from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IdeaCreate(BaseModel):
    title: str
    description: str
    category: str


class StatusUpdate(BaseModel):
    status: str
    comment: Optional[str] = None


class UserSummary(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True


class IdeaSummary(BaseModel):
    id: int
    title: str
    status: str
    category: str
    created_at: datetime

    class Config:
        orm_mode = True


class IdeaDetail(BaseModel):
    id: int
    title: str
    description: str
    category: str
    status: str
    created_at: datetime
    updated_at: datetime
    submitter: UserSummary

    class Config:
        orm_mode = True
