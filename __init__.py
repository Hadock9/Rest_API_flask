from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from .resources import BookListResource, BookResource

def create_app():
    app = Flask(__name__)
    
    # Налаштування Swagger
    app.config['SWAGGER'] = {
        'title': 'Library API',
        'uiversion': 3,
        'specs_route': '/api/docs/'
    }
    
    # Ініціалізація Swagger
    swagger = Swagger(app, template={
        "swagger": "3.0",
        "info": {
            "title": "Library API",
            "description": "API for managing books in a library",
            "version": "1.0.0"
        },
        "definitions": {
            "Book": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "year": {"type": "integer"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                }
            },
            "BookCreate": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "year": {"type": "integer"}
                },
                "required": ["title", "author", "year"]
            }
        }
    })
    
    # Ініціалізація API
    api = Api(app)
    
    # Реєстрація ресурсів
    api.add_resource(BookListResource, '/api/books')
    api.add_resource(BookResource, '/api/books/<int:book_id>')
    
    return app
