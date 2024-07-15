from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
maincompany_blueprint = func.Blueprint('maincompany', __name__)



@maincompany_blueprint.route('maincompany', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def add_maincompany(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO maincompany (companyname, datecreated, logo, other) VALUES (%s, CURRENT_TIMESTAMP, %s, %s)',
            (data['companyname'], data['logo'], data['other'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'MainCompany added'}).get_data(as_text=True), mimetype="application/json", status_code=201)

@maincompany_blueprint.route('maincompany', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_maincompanies(req: func.HttpRequest):
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM maincompany')
        maincompanies = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(maincompanies).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@maincompany_blueprint.route('maincompany-getbyid', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_maincompany_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM maincompany WHERE maincompanyid = %s', (id,))
        maincompany = cursor.fetchone()
        cursor.close()
        conn.close()
        response_data = jsonify(maincompany).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@maincompany_blueprint.route('maincompany-update', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def update_maincompany(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
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
        return func.HttpResponse(jsonify({'status': 'MainCompany updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@maincompany_blueprint.route('maincompany', methods=['DELETE'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def delete_maincompany(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM maincompany WHERE maincompanyid = %s', (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'MainCompany deleted'}).get_data(as_text=True), mimetype="application/json", status_code=200)



