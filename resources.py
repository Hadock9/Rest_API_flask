from flask_restful import Resource, reqparse
from flask import jsonify
from marshmallow import ValidationError
from flasgger import swag_from

from .models import books, Book
from .schemas import BookSchema, BookCreateSchema

book_schema = BookSchema()
book_create_schema = BookCreateSchema()

class BookListResource(Resource):
    @swag_from({
        'tags': ['books'],
        'description': 'Get all books',
        'parameters': [
            {
                'name': 'limit',
                'in': 'query',
                'type': 'integer',
                'default': 10,
                'description': 'Number of books to return'
            },
            {
                'name': 'offset',
                'in': 'query',
                'type': 'integer',
                'default': 0,
                'description': 'Number of books to skip'
            }
        ],
        'responses': {
            '200': {
                'description': 'List of books',
                'schema': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/Book'
                    }
                }
            }
        }
    })
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, default=10)
        parser.add_argument('offset', type=int, default=0)
        args = parser.parse_args()

        result = books[args['offset']:args['offset'] + args['limit']]
        return jsonify([book.to_dict() for book in result])

    @swag_from({
        'tags': ['books'],
        'description': 'Create a new book',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    '$ref': '#/definitions/BookCreate'
                }
            }
        ],
        'responses': {
            '201': {
                'description': 'Book created',
                'schema': {
                    '$ref': '#/definitions/Book'
                }
            },
            '400': {
                'description': 'Validation error'
            }
        }
    })
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, help="Title cannot be blank")
        parser.add_argument('author', required=True, help="Author cannot be blank")
        parser.add_argument('year', type=int, required=True, help="Year cannot be blank")
        args = parser.parse_args()

        try:
            validated = book_create_schema.load(args)
        except ValidationError as err:
            return jsonify(err.messages), 400

        new_id = max(book.id for book in books) + 1 if books else 1
        new_book = Book(new_id, validated['title'], validated['author'], validated['year'])
        books.append(new_book)
        return jsonify(new_book.to_dict()), 201

class BookResource(Resource):
    @swag_from({
        'tags': ['books'],
        'description': 'Get a book by ID',
        'parameters': [
            {
                'name': 'book_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the book'
            }
        ],
        'responses': {
            '200': {
                'description': 'Book found',
                'schema': {
                    '$ref': '#/definitions/Book'
                }
            },
            '404': {
                'description': 'Book not found'
            }
        }
    })
    def get(self, book_id):
        book = next((book for book in books if book.id == book_id), None)
        if book is None:
            return {'message': 'Book not found'}, 404
        return jsonify(book.to_dict())

    @swag_from({
        'tags': ['books'],
        'description': 'Delete a book',
        'parameters': [
            {
                'name': 'book_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the book'
            }
        ],
        'responses': {
            '200': {
                'description': 'Book deleted'
            },
            '404': {
                'description': 'Book not found'
            }
        }
    })
    def delete(self, book_id):
        global books
        book = next((book for book in books if book.id == book_id), None)
        if book is None:
            return {'message': 'Book not found'}, 404
        books = [b for b in books if b.id != book_id]
        return {'message': 'Book deleted'} 