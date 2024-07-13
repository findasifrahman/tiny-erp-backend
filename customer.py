from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2
customer_blueprint = Blueprint('customer', __name__)


@customer_blueprint.route('/customer', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def add_customer():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO customers (maincompanyid, customercompany, companycontactperson, contactnumber1, contactnumber2, address, olddue, createdat) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)',
        (data['maincompanyid'], data['customercompany'], data['companycontactperson'], data['contactnumber1'],data['contactnumber2'], data['address'],data['olddue'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User added'}), 201

@customer_blueprint.route('/customer/<maincompanyid>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
def get_customers(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM customers where maincompanyid = %s', (maincompanyid))
    users = cursor.fetchall()
    print("users--",users)
    cursor.close()
    conn.close()
    return jsonify(users), 200

@customer_blueprint.route('/customer/getbyid', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_customer_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM customers WHERE customerid = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user), 200

@customer_blueprint.route('/customer/update', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def update_customer():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE customers SET maincompanyid = %s, customercompany = %s, companycontactperson = %s, contactnumber1 = %s, contactnumber2 = %s, address = %s, olddue = %s WHERE customerid = %s',
        (data['maincompanyid'], data['customercompany'], data['companycontactperson'], data['contactnumber1'],data['contactnumber2'], data['address'],data['olddue'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User updated'}), 200

@customer_blueprint.route('/customer', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
@token_required
def delete_customer():
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
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
        return jsonify({'message': str(e)}), 400
    finally:
        cursor.close()
        conn.close()
        if not error:
            return jsonify({'status': 'Customer deleted', 'data': roles}), 200

    
