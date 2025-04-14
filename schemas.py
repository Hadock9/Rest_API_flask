from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class BookBase(BaseModel):
    title: str
    author: str
    year: int

class BookCreate(BookBase):
    pass

class BookSchema(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BooksResponse(BaseModel):
    items: List[BookSchema]
    next_cursor: Optional[int] = None
