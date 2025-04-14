from fastapi import APIRouter, HTTPException
from typing import List
from .models import books
from .schemas import Book, BookCreate

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=List[Book])
async def get_all_books():
    return books

@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: str):
    book = next((book for book in books if book["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/", response_model=Book, status_code=201)
async def add_book(book: BookCreate):
    new_id = str(len(books) + 1)
    new_book = Book(
        id=new_id,
        title=book.title,
        author=book.author,
        year=book.year
    )
    books.append(new_book.model_dump())
    return new_book

@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str):
    global books
    book = next((book for book in books if book["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    books = [b for b in books if b["id"] != book_id]
    return None
