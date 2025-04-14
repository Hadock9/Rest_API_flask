from flask import Blueprint

book_bp = Blueprint("books",
                    __name__,
                    url_prefix="/book",
                    template_folder="templates/books"
                    )

from . import views