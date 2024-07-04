from flask import Blueprint, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

maincompany_blueprint = Blueprint('maincompany', __name__)

load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )
    return conn

@maincompany_blueprint.route('/maincompany', methods=['POST'])
def add_maincompany():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO maincompany (CompanyName, Date_created, logo, other) VALUES (%s, CURRENT_TIMESTAMP, %s, %s)',
        (data['CompanyName'], data['logo'], data['other'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'MainCompany added'}), 201

@maincompany_blueprint.route('/maincompany', methods=['GET'])
def get_maincompanies():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM maincompany')
    maincompanies = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(maincompanies), 200

@maincompany_blueprint.route('/maincompany/<int:id>', methods=['GET'])
def get_maincompany_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM maincompany WHERE MainCompanyID = %s', (id,))
    maincompany = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(maincompany), 200

@maincompany_blueprint.route('/maincompany/<int:id>', methods=['PUT'])
def update_maincompany(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE maincompany SET CompanyName = %s, logo = %s, other = %s WHERE MainCompanyID = %s',
        (data['CompanyName'], data['logo'], data['other'], id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'MainCompany updated'}), 200

@maincompany_blueprint.route('/maincompany/<int:id>', methods=['DELETE'])
def delete_maincompany(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM maincompany WHERE MainCompanyID = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'MainCompany deleted'}), 200
