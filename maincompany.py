from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required

import azure.functions as func
maincompany_blueprint = func.Blueprint('maincompany', __name__)



@maincompany_blueprint.route('/maincompany', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
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
@token_required
def get_maincompanies():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM maincompany')
    maincompanies = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(maincompanies), 200

@maincompany_blueprint.route('/maincompany/getbyid', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_maincompany_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM maincompany WHERE maincompanyid = %s', (id,))
    maincompany = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(maincompany), 200

@maincompany_blueprint.route('/maincompany/update', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
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

@maincompany_blueprint.route('/maincompany', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
@token_required
def delete_maincompany():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM maincompany WHERE maincompanyid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'MainCompany deleted'}), 200


