import uuid
import logging 
from flask import jsonify, request 
from werkzeug.exceptions import HTTPException

ERROR_BASE = "https://api.example.com/probs"

class ApiProblem(Exception):
    def __init__(self, status, title, detail=None, type_path=None, **extra):
        super().__init__(title)
        self.status = status
        self.title = title
        self.detail = detail
        self.type_path = type_path
        self.extra = extra

def make_problem_response(status, title, detail=None, type_path=None, **extra):
    body = {
        "type": f"{ERROR_BASE}/{type_path}" if type_path else "about:blank",
        "title": title,
        "status": status,
        "instance": request.path,
        "trace_id": str(uuid.uuid4())
    }
    if detail:
        body["detail"] = detail

    body.update(extra)

    resp = jsonify(body)
    resp.status_code = status
    resp.headers["Content-Type"] = "application/problem+json"
    return resp

def register_error_handlers(app):
    @app.errorhandler(ApiProblem)
    def handle_api_problem(e):
        return make_problem_response(
            status=e.status,
            title=e.title,
            etail=e.detail,
            type_path=e.type_path,
            **e.extra
        )
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return make_problem_response(
            status=e.code,
            title=e.name,
            detail=e.description
        )

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        logging.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        return make_problem_response(
            status=500,
            title="Internal Server Error",
            detail="Da co loi he thong xa ra. Vui long lien he quan tri vien."
        )