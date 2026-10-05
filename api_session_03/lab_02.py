from flask import Flask, jsonify
from errors import ApiProblem, register_error_handlers

app = Flask(__name__)

register_error_handlers(app)

resources_db = {
    1: {"id": 1, "name": "Still in love 1"}
}

@app.get("/resources/<int:id>")
def get_resource(id):
    res = resources_db.get(id)
    if not res:
        raise ApiProblem(
            status=404,
            title="Resource not found",
            detail=f"Resource with id {id} does not exist",
            type_path="resource-not-found",
            resource_id=id
        )
    return jsonify(res)

@app.get("/users/<int:id>")
def get_user(id):
    raise ApiProblem(
        status=404,
        title="User not found",
        type_path="user-not-found",
        resource_id=id
    )

@app.get("/crash")
def crash():
    return 1 / 0

if __name__ == "__main__":
    app.run(debug=True)