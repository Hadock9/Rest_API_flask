from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic_mongo import PydanticObjectId
from datetime import datetime

from .database import get_database
from .schemas import BookSchema, BookCreateSchema, BooksResponse

router = APIRouter()

@router.get("/books", response_model=BooksResponse)
async def get_all_books(
    cursor: Optional[str] = None,
    limit: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    query = {}
    if cursor:
        query["_id"] = {"$gt": PydanticObjectId(cursor)}
    
    cursor = db.books.find(query).sort("_id", 1).limit(limit)
    books = await cursor.to_list(length=limit)
    
    next_cursor = None
    if books:
        next_cursor = str(books[-1]["_id"])
    
    return BooksResponse(
        items=[BookSchema(
            id=book["_id"],
            title=book["title"],
            author=book["author"],
            year=book["year"],
            created_at=book.get("created_at", datetime.utcnow()),
            updated_at=book.get("updated_at", datetime.utcnow())
        ) for book in books],
        next_cursor=next_cursor
    )

@router.get("/books/{book_id}", response_model=BookSchema)
async def get_book(book_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    book = await db.books.find_one({"_id": PydanticObjectId(book_id)})
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return BookSchema(
        id=book["_id"],
        title=book["title"],
        author=book["author"],
        year=book["year"],
        created_at=book.get("created_at", datetime.utcnow()),
        updated_at=book.get("updated_at", datetime.utcnow())
    )

@router.post("/books", response_model=BookSchema, status_code=201)
async def add_book(book: BookCreateSchema, db: AsyncIOMotorDatabase = Depends(get_database)):
    book_data = book.dict()
    book_data["created_at"] = datetime.utcnow()
    book_data["updated_at"] = datetime.utcnow()
    
    result = await db.books.insert_one(book_data)
    book_data["_id"] = result.inserted_id
    
    return BookSchema(
        id=book_data["_id"],
        title=book_data["title"],
        author=book_data["author"],
        year=book_data["year"],
        created_at=book_data["created_at"],
        updated_at=book_data["updated_at"]
    )

@router.delete("/books/{book_id}")
async def delete_book(book_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    result = await db.books.delete_one({"_id": PydanticObjectId(book_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}
