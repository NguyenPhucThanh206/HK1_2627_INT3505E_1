"""Contract test: response thật của Flask phải khớp openapi.yaml.
Trả lời câu hỏi Lab 2: spec pass Spectral nhưng code trả sai field -> test này bắt được
(Spectral chỉ lint file spec, không chạy code). Không phụ thuộc fixture sample_book.
Chạy: python -m pytest -v tests/test_contract_openapi.py
"""
import copy
from pathlib import Path

import pytest
import yaml
from jsonschema import ValidationError, validate

SPEC = yaml.safe_load((Path(__file__).resolve().parent.parent / "openapi.yaml").read_text(encoding="utf-8"))
SCHEMAS = SPEC["components"]["schemas"]


def to_jsonschema(node):
    """OpenAPI 3.0 -> JSON Schema: `nullable: true` => type [x, 'null']."""
    node = copy.deepcopy(node)

    def walk(n):
        if isinstance(n, dict):
            if n.pop("nullable", False) and "type" in n:
                n["type"] = [n["type"], "null"]
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)

    walk(node)
    return node


BOOK, ERROR = to_jsonschema(SCHEMAS["Book"]), to_jsonschema(SCHEMAS["Error"])


def declared(path, method):
    return {int(s) for s in SPEC["paths"][path][method]["responses"]}


def create(client, **extra):
    payload = {"title": "Contract Book", "author": "Tester", "year": 2021, **extra}
    r = client.post("/books", json=payload)
    assert r.status_code == 201, r.get_json()
    return r.get_json()


def test_list_books_matches_spec(client):
    create(client)
    create(client, year=None)  # year null cũng phải hợp lệ
    r = client.get("/books")
    assert r.status_code in declared("/books", "get")
    assert len(r.get_json()) == 2
    for item in r.get_json():
        validate(item, BOOK)


def test_get_book_matches_spec(client):
    book = create(client)
    r = client.get(f"/books/{book['id']}")
    assert r.status_code in declared("/books/{id}", "get")
    validate(r.get_json(), BOOK)
    assert isinstance(r.get_json()["year"], int)   # lỗi 3 của lab: year phải là int, không phải str


def test_create_book_matches_spec(client):
    r = client.post("/books", json={"title": "DDIA", "author": "Kleppmann", "year": 2017})
    assert r.status_code == 201 and 201 in declared("/books", "post")
    validate(r.get_json(), BOOK)


def test_put_matches_spec(client):
    book = create(client)
    r = client.put(f"/books/{book['id']}", json={"title": "New", "author": "A", "year": 2000})
    assert r.status_code in declared("/books/{id}", "put")
    validate(r.get_json(), BOOK)


@pytest.mark.parametrize("path,method,body,status", [
    ("/books/9999", "get", None, 404),
    ("/books/abc", "get", None, 400),
    ("/books/9999", "delete", None, 404),
    ("/books", "post", {"author": "X"}, 400),
])
def test_error_bodies_match_spec(client, path, method, body, status):
    r = getattr(client, method)(path, **({"json": body} if body is not None else {}))
    assert r.status_code == status
    spec_path = "/books/{id}" if path.startswith("/books/") else path
    assert status in declared(spec_path, method)
    validate(r.get_json(), ERROR)


def test_duplicate_isbn_409_matches_spec(client):
    create(client, isbn="9781617295850")
    r = client.post("/books", json={"title": "Dup", "author": "A", "isbn": "9781617295850"})
    assert r.status_code == 409 and 409 in declared("/books", "post")
    validate(r.get_json(), ERROR)


def test_delete_204_has_empty_body(client):
    book = create(client)
    r = client.delete(f"/books/{book['id']}")
    assert r.status_code == 204 and r.data == b""
    assert "content" not in SPEC["paths"]["/books/{id}"]["delete"]["responses"]["204"]


# --- Mutation: chứng minh schema validation thật sự bắt lỗi ---
def test_catches_renamed_field(client):
    body = create(client)
    body["fullTitle"] = body.pop("title")
    with pytest.raises(ValidationError):
        validate(body, BOOK)


def test_catches_number_to_string(client):
    body = create(client)
    body["year"] = "2021"
    with pytest.raises(ValidationError):
        validate(body, BOOK)


def test_response_extra_field_blocked(client):
    body = create(client)
    body["password_hash"] = "x"
    with pytest.raises(ValidationError):
        validate(body, BOOK)
