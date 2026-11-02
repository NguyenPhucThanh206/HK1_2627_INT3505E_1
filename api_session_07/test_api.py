import pytest
from factory import create_app
from api.extensions import db

@pytest.fixture
def client():
    app = create_app()
    # Dùng database trên RAM để test độc lập, chạy nhanh
    app.config.update({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200

def test_empty_orders(client):
    response = client.get("/api/v1/orders")
    assert response.status_code == 200
    assert response.json["items"] == []