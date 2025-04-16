from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from datetime import timedelta
from .auth import (
    Token, User, UserInDB, get_current_active_user,
    create_access_token, create_refresh_token, get_user,
    verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
)
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

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": username})
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/books", response_model=BooksResponse)
async def get_all_books(
    cursor: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
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
async def get_book(
    book_id: str,
    current_user: User = Depends(get_current_active_user)
):
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
async def add_book(
    book: BookCreateSchema,
    current_user: User = Depends(get_current_active_user)
):
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
async def delete_book(
    book_id: str,
    current_user: User = Depends(get_current_active_user)
):
    result = await db.books.delete_one({"_id": PydanticObjectId(book_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}
