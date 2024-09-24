import pytest
from main import app, db, Customer, Order

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_add_customer(client):
    response = client.post('/customers', json={'name': 'John Doe', 'code': '+254701234567'})
    assert response.status_code == 201
    assert response.json == {"message": "Customer added!"}

def test_add_order(client):
    client.post('/customers', json={'name': 'John Doe', 'code': '+254701234567'})
    response = client.post('/orders', json={'item': 'Book', 'amount': 20.5, 'customer_id': 1})
    assert response.status_code == 201
    assert response.json == {"message": "Order added!"}
