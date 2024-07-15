from flask import request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
customer_blueprint = func.Blueprint('customer', __name__)


@customer_blueprint.route('customer', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def add_customer(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO customers (maincompanyid, customercompany, companycontactperson, contactnumber1, contactnumber2, address, olddue, createdat) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)',
            (data['maincompanyid'], data['customercompany'], data['companycontactperson'], data['contactnumber1'],data['contactnumber2'], data['address'],data['olddue'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Customer added'}).get_data(as_text=True), mimetype="application/json", status_code=201)


@customer_blueprint.route('customer/{maincompanyid}', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
def get_customers(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM customers where maincompanyid = %s', (maincompanyid))
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(users).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@customer_blueprint.route('customer-getbyid', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_customer_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM customers WHERE customerid = %s', (id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        response_data = jsonify(user).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@customer_blueprint.route('customer-update', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def update_customer(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE customers SET maincompanyid = %s, customercompany = %s, companycontactperson = %s, contactnumber1 = %s, contactnumber2 = %s, address = %s, olddue = %s WHERE customerid = %s',
            (data['maincompanyid'], data['customercompany'], data['companycontactperson'], data['contactnumber1'],data['contactnumber2'], data['address'],data['olddue'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Customer updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@customer_blueprint.route('customer', methods=['DELETE'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def delete_customer(req: func.HttpRequest):
    id = req.params.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM customers WHERE customerid = %s', (id,))
            conn.commit()
            
            # Fetch the updated list of sales order details
            cursor.execute('SELECT * FROM customers where maincompanyid = %s', (maincompanyid))
            roles = cursor.fetchall()
        except psycopg2.Error as e:
            error =True
            conn.rollback()
            print("error test is --",e)
            return func.HttpResponse(jsonify({'message': str(e)}).get_data(as_text=True), mimetype="application/json", status_code=400)

        finally:
            cursor.close()
            conn.close()
            if not error:
                return func.HttpResponse(jsonify({'status': 'Customer Deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)

        
