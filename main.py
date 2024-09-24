from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import africastalking
from datetime import datetime
from africastalking import initialize

app = Flask(__name__)

# Africa's Talking API setup
africastalking.initialize(username='sandbox', api_key='atsk_5b24f67d18b468e267cd814d09283c306b256bd2165f3c5043dfad6761e8223d8b35136b') 
sms = africastalking.SMS

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Customer and Order Models
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(20), nullable=False, unique=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

# API Routes
@app.route('/customers', methods=['GET', 'POST', 'OPTIONS'])
def handle_customers():
    if request.method == 'POST':
        data = request.get_json()
        new_customer = Customer(name=data['name'], code=data['code'])
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"message": "Customer added!"}), 201

    elif request.method == 'GET':
        customers = Customer.query.all()
        return jsonify([{"id": customer.id, "name": customer.name, "code": customer.code} for customer in customers]), 200

    elif request.method == 'OPTIONS':
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response

@app.route('/orders', methods=['GET', 'POST', 'OPTIONS'])
def handle_orders():
    if request.method == 'POST':
        data = request.get_json()
        new_order = Order(item=data['item'], amount=data['amount'], customer_id=data['customer_id'])
        db.session.add(new_order)
        db.session.commit()

        # Send SMS notification
        customer = Customer.query.get(new_order.customer_id)
        send_sms_alert(customer.code, new_order.item, new_order.amount)

        return jsonify({"message": "Order added!"}), 201

    elif request.method == 'GET':
        orders = Order.query.all()
        return jsonify([{"id": order.id, "item": order.item, "amount": order.amount, "time": order.time.isoformat(), "customer_id": order.customer_id} for order in orders]), 200

    elif request.method == 'OPTIONS':
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response

def send_sms_alert(customer_code, item, amount):
    message = f"Order received: {item} worth {amount}. Thank you!"
    recipients = [customer_code]  # Customer phone numbers
    response = sms.send(message, recipients)
    print(response)

# Database initialization function
def init_db():
    with app.app_context():  # Create application context
        db.create_all()  # Create the database tables

if __name__ == '__main__':
    init_db()  # Initialize the database on startup
    app.run(debug=True)  # Run the Flask application
