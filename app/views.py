from flask import Flask, jsonify, request, abort
from marshmallow import Schema, fields, ValidationError
from . import app
import uuid


@app.route('/')
def index():
    return "Hello"


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


