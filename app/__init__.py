from flask import Flask


app = Flask(__name__)
from . import views

from .books import book_bp

app.register_blueprint(book_bp)