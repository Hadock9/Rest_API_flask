from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from marshmallow import ValidationError

from .models import books
from .schemas import BookSchema

router = APIRouter()
schema = BookSchema()

@router.get("/books")
async def get_all_books():
    return JSONResponse(content=books)

@router.get("/books/{book_id}")
async def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return JSONResponse(content=book)
    raise HTTPException(status_code=404, detail="Book not found")

@router.post("/books")
async def add_book(request: Request):
    data = await request.json()
    try:
        validated = schema.load(data)
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)

    for book in books:
        if book["id"] == validated["id"]:
            raise HTTPException(status_code=400, detail="Book with this ID already exists")

    books.append(validated)
    return JSONResponse(content=validated, status_code=201)

@router.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return JSONResponse(content={"message": "Book deleted"})
    raise HTTPException(status_code=404, detail="Book not found")
