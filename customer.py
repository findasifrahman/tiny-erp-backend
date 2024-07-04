from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

user_blueprint = Blueprint('users', __name__)

load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )
    return conn

@user_blueprint.route('/customers', methods=['POST'])
@cross_origin()  # Enable CORS for this route
def add_user():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO customers (maincompanyid, customercompany, companycontactperson, contactnumber1, contactnumber2, address, olddue, createdat) VALUES (%s, %s, %s, %s, %s, %s, %s CURRENT_TIMESTAMP)',
        (data['maincompanyid'], data['username'], data['password'], data['roleid'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User added'}), 201

@user_blueprint.route('/customers', methods=['GET'])
@cross_origin()  # Enable CORS for this route
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM customers')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users), 200

@user_blueprint.route('/customers/<int:id>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
def get_user_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM customers WHERE customerid = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user), 200

@user_blueprint.route('/customers/<int:id>', methods=['PUT'])
@cross_origin()  # Enable CORS for this route
def update_user(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE customers SET maincompanyid = %s, customercompany = %s, companycontactperson = %s, contactnumber1 = %s contactnumber2 = %s, address = %s, oldvalue = %s, createdat = %s WHERE customerid = %s',
        (data['maincompanyid'], data['customercompany'], data['companycontactperson'], data['contactnumber1'],data['contactnumber2'], data['address'],data['olddue'],data['createdat'], id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User updated'}), 200

@user_blueprint.route('/customers/<int:id>', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM customres WHERE customerid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User deleted'}), 200
