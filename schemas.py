from marshmallow import Schema, fields, validate, ValidationError

class BookSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    author = fields.Str(required=True, validate=validate.Length(min=1))
    year = fields.Int(required=True)
