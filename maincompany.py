from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
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
@cross_origin()  # Enable CORS for this route
def add_maincompany():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO maincompany (companyname, datecreated, logo, other) VALUES (%s, CURRENT_TIMESTAMP, %s, %s)',
        (data['companyname'], data['logo'], data['other'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'MainCompany added'}), 201

@maincompany_blueprint.route('/maincompany', methods=['GET'])
@cross_origin()  # Enable CORS for this route
def get_maincompanies():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM maincompany')
    maincompanies = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(maincompanies), 200

@maincompany_blueprint.route('/maincompany/<int:id>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
def get_maincompany_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM maincompany WHERE maincompanyid = %s', (id,))
    maincompany = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(maincompany), 200

@maincompany_blueprint.route('/maincompany/update', methods=['POST'])
@cross_origin()  # Enable CORS for this route
def update_maincompany():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    #print("data rcvd in put",data)
    cursor.execute(
        'UPDATE maincompany SET companyname = %s, logo = %s, other = %s WHERE maincompanyid = %s',
        (data['companyname'], data['logo'], data['other'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'MainCompany updated'}), 200

@maincompany_blueprint.route('/maincompany/<int:id>', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
def delete_maincompany(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM maincompany WHERE maincompanyid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'MainCompany deleted'}), 200
