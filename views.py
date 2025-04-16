from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from .models import Book, SessionLocal
from .schemas import BookSchema, BookCreateSchema
from pydantic import BaseModel

router = APIRouter(prefix="/books", tags=["books"])

# Залежність для отримання сесії бази даних
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PaginatedResponse(BaseModel):
    items: List[Book]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

@router.get("/", response_model=PaginatedResponse)
async def get_all_books(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page")
):
    start = (page - 1) * size
    end = start + size
    paginated_items = db.query(Book).offset(start).limit(size).all()
    
    total = db.query(Book).count()
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=paginated_items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )

@router.get("/books/{book_id}", response_model=BookSchema)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/books", response_model=BookSchema, status_code=201)
async def add_book(book: BookCreateSchema, db: Session = Depends(get_db)):
    db_book = Book(
        title=book.title,
        author=book.author,
        year=book.year
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/books/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}
