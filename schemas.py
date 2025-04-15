from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from pydantic_mongo import PydanticObjectId

class BookBase(BaseModel):
    title: str
    author: str
    year: int

class BookCreate(BookBase):
    pass

class BookSchema(BookBase):
    id: PydanticObjectId
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            PydanticObjectId: str
        }

class BooksResponse(BaseModel):
    items: List[BookSchema]
    next_cursor: Optional[str] = None
