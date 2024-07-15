#officeipurchasetemlist: officeipurchasetemlistid SERIAL PRIMARY KEY, maincompanyid int not null unchangeable, itemname varchar(256) not null, price INT not null, description TEXT,  
#createdat TIMESTAMP

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
officepurchaseitemlist_blueprint = func.Blueprint('officepurchaseitemlist', __name__)


@officepurchaseitemlist_blueprint.route('officepurchaseitemlist', methods=['POST'])
#@cross_origin()
#@token_required
def add_officepurchaseitemlist(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO officepurchaseitemlist (maincompanyid, itemname, price, description, createdat) 
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)''',
            (data['maincompanyid'], data['itemname'], data['price'], data['description'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Office Purchase Item added'}).get_data(as_text=True), mimetype="application/json", status_code=201)

@officepurchaseitemlist_blueprint.route('officepurchaseitemlist/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_officepurchaseitemlists(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM officepurchaseitemlist where maincompanyid = %s', (maincompanyid,))
        officepurchaseitemlists = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(officepurchaseitemlists).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@officepurchaseitemlist_blueprint.route('officepurchaseitemlist-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_officepurchaseitemlist_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM officepurchaseitemlist WHERE officepurchaseitemlistid = %s', (id,))
        officepurchaseitemlist = cursor.fetchone()
        cursor.close()
        conn.close()
        if not officepurchaseitemlist:
            return func.HttpResponse(jsonify({'status': 'Office Purchase Item List not found'}).get_data(as_text=True), mimetype="application/json", status_code=404)

        response_data = jsonify(officepurchaseitemlist).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@officepurchaseitemlist_blueprint.route('officepurchaseitemlist-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_officepurchaseitemlist(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE officepurchaseitemlist SET itemname = %s, price = %s, description = %s 
            WHERE officepurchaseitemlistid = %s''',
            (data['itemname'], data['price'], data['description'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Office Purchase Item List updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@officepurchaseitemlist_blueprint.route('officepurchaseitemlist', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_officepurchaseitemlist(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM officepurchaseitemlist WHERE officepurchaseitemlistid = %s', (id,))
            conn.commit()
            
            cursor.execute('SELECT * FROM officepurchaseitemlist where maincompanyid = %s', (maincompanyid))
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
                return func.HttpResponse(jsonify({'status': 'officepurchaseitemlist deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)
