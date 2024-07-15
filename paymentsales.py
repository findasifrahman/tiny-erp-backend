#paymentsales: paymentid SERIAL PRIMARY KEY, maincompanyid int not null unchangeable, customerid INT NOT NULL, paymentdate DATE NOT NULL, 
#amount DECIMAL(10, 2) NOT NULL,receivedby varchar(256) not null, createdat TIMESTAMP

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
paymentsales_blueprint = func.Blueprint('paymentsales', __name__)


@paymentsales_blueprint.route('paymentsales', methods=['POST'])
#@cross_origin()
#@token_required
def add_paymentsales(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO paymentsales (maincompanyid, customerid, customercompany, paymentdate, amount, recievedbyid, receivedby, salesorderid,description, createdat) 
            VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, CURRENT_TIMESTAMP)''',
            (data['maincompanyid'], data['customerid'], data['customercompany'], data['paymentdate'], data['amount'], data['recievedbyid'], data['receivedby'], data['salesorderid'], data['description'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Payment Sales added'}).get_data(as_text=True), mimetype="application/json", status_code=201)

@paymentsales_blueprint.route('paymentsales/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_paymentsales(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = '''
        SELECT * FROM paymentsales where maincompanyid = %s AND paymentdate >= NOW() - INTERVAL '3 MONTHS' ORDER BY paymentdate DESC
        '''
        cursor.execute(query, (maincompanyid))
        paymentsales = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(paymentsales).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@paymentsales_blueprint.route('paymentsales-getall/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_paymentsales_all(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM paymentsales where maincompanyid = %s', (maincompanyid))
        paymentsales = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(paymentsales).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@paymentsales_blueprint.route('paymentsales-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_paymentsales_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM paymentsales WHERE paymentid = %s', (id,))
        paymentsales = cursor.fetchone()
        cursor.close()
        conn.close()
        if not paymentsales:
            return func.HttpResponse(jsonify({'status': 'Payment Sales not found'}).get_data(as_text=True), mimetype="application/json", status_code=404)

        response_data = jsonify(paymentsales).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@paymentsales_blueprint.route('paymentsales-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_paymentsales(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        print("data is --",data)
        cursor.execute(
            '''UPDATE paymentsales SET customerid = %s,customercompany = %s, paymentdate = %s, amount = %s,recievedbyid = %s, receivedby = %s, salesorderid = %s, description = %s 
            WHERE paymentid = %s''',
            (data['customerid'], data['customercompany'], data['paymentdate'], data['amount'],data['recievedbyid'], data['receivedby'],data['salesorderid'], data['description'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Payment Sales updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@paymentsales_blueprint.route('paymentsales', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_paymentsales(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM paymentsales WHERE paymentid = %s', (id,))
            conn.commit()
            
            query = '''
            SELECT * FROM paymentsales where maincompanyid = %s AND paymentdate >= NOW() - INTERVAL '3 MONTHS' ORDER BY paymentdate DESC
            '''
            cursor.execute(query, (maincompanyid))
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
                return func.HttpResponse(jsonify({'status': 'paymentsales deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)
