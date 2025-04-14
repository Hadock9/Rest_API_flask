from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from .models import Book, SessionLocal
from .schemas import BookSchema, BookCreateSchema, BooksResponse

router = APIRouter()

# Залежність для отримання сесії бази даних
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/books", response_model=BooksResponse)
async def get_all_books(
    cursor: Optional[int] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Book)
    
    if cursor:
        query = query.filter(Book.id > cursor)
    
    books = query.order_by(Book.id).limit(limit).all()
    
    next_cursor = None
    if books:
        next_cursor = books[-1].id
    
    return BooksResponse(
        items=books,
        next_cursor=next_cursor
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
