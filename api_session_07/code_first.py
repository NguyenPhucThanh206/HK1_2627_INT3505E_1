from flask import Flask
from flask.views import MethodView
from flask_smorest import Api, Blueprint
from marshmallow import Schema, fields

app = Flask(__name__)
app.config["API_TITLE"] = "Book API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

books_db = [
    {"id": 1, "title": "newgame+1", "author": "Me"},
    {"id": 2, "title": "newgame+2", "author": "Me"}
]

class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)

blp = Blueprint("books", __name__, url_prefix="/books", description="Các thao tác với sách")

@blp.route("/")
class BookList(MethodView):
    @blp.response(200, BookSchema(many=True))
    def get(self):
        return books_db

api.register_blueprint(blp)

if __name__ == "__main__":
    app.run(debug=True)