from flask import Flask, jsonify, request, abort
from marshmallow import Schema, fields, ValidationError
import uuid
from . import book_bp

class BookSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    year = fields.Int(required=True)

book_schema = BookSchema()
books_schema = BookSchema(many=True)

books = [
    {
        "id": 1,
        "title": "1984",
        "author": "George Orwell",
        "year": 1949
    },
    {
        "id": 2,
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "year": 1932
    },
    {
        "id": 3,
        "title": "Fahrenheit 451",
        "author": "Ray Bradbury",
        "year": 1953
    }
]

@book_bp.route('/', methods=['GET'])
def get_books():
    return jsonify(books), 200

@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((book for book in books if book["id"] == book_id), None)
    if not book:
        abort(404, description="Book not found")
    return jsonify(book), 200

@book_bp.route('/add_book', methods=['POST'])
def add_book():
    try:
        data = book_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    data["id"] = str(uuid.uuid4())  # Generate a unique ID
    books.append(data)
    return jsonify(data), 201

@book_bp.route('/delete/<string:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = next((book for book in books if book["id"] == book_id), None)
    if not book:
        abort(404, description="Book not found")

    books = [b for b in books if b["id"] != book_id]
    return jsonify({"message": "Book deleted"}), 200