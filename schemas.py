from pydantic import BaseModel, Field

class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    year: int

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: str

    class Config:
        from_attributes = True
