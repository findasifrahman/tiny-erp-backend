#salesorderdetails: (salesorderdetailid serial primary key, maincompanyid int not null unchangeable), salesorderid INT NOT NULL, productcategoryid INT NOT NULL, 
#productcategoryname varchar(256) not null, productsubcategoryid INT not null, productsubcategoryname varchar(256) not null,  quantity INT NOT NULL, unit VARCHAR(12) not null, 
#unitprice DECIMAL(10, 2) NOT NULL, totaldetailprice DECIMAL(10, 2) NOT NULL, description TEXT createdat TIMESTAMP

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from auth import token_required
from dbcon import get_db_connection
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
salesorderdetails_blueprint = func.Blueprint('salesorderdetails', __name__)

@salesorderdetails_blueprint.route('salesorderdetails', methods=['POST'])
#@cross_origin()
#@token_required
def add_salesorderdetail(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO salesorderdetails (maincompanyid, salesorderid, productcategoryid, productcategoryname, productsubcategoryid, productsubcategoryname, quantity, unit, unitprice, totaldetailprice, description, createdat) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
            (data['maincompanyid'], data['salesorderid'], data['productcategoryid'], data['productcategoryname'], data['productsubcategoryid'], data['productsubcategoryname'], data['quantity'], data['unit'], data['unitprice'], data['totaldetailprice'], data['description'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Sales Order Detail added'}).get_data(as_text=True), mimetype="application/json", status_code=201)

@salesorderdetails_blueprint.route('salesorderdetails/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_salesorderdetails(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM salesorderdetails where maincompanyid = %s', (maincompanyid))
        salesorderdetails = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(salesorderdetails).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)
    
@salesorderdetails_blueprint.route('salesorderdetails-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_salesorderdetail_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM salesorderdetails WHERE salesorderdetailid = %s', (id,))
        salesorderdetail = cursor.fetchone()
        cursor.close()
        conn.close()
        if not salesorderdetail:
            return func.HttpResponse(jsonify({'message': 'Sales Order Detail not found'}).get_data(as_text=True), mimetype="application/json", status_code=404)
        return func.HttpResponse(salesorderdetail, mimetype="application/json", status_code=200)

@salesorderdetails_blueprint.route('salesorderdetails-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_salesorderdetail(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE salesorderdetails SET salesorderid = %s, productcategoryid = %s, productcategoryname = %s, productsubcategoryid = %s, productsubcategoryname = %s, quantity = %s, unit = %s, unitprice = %s, totaldetailprice = %s, description = %s
            WHERE salesorderdetailid = %s''',
            (data['salesorderid'], data['productcategoryid'], data['productcategoryname'], data['productsubcategoryid'], data['productsubcategoryname'], data['quantity'], data['unit'], data['unitprice'], data['totaldetailprice'], data['description'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Sales Order Detail updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)


@salesorderdetails_blueprint.route('salesorderdetails', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_salesorderdetail(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM salesorderdetails WHERE salesorderdetailid = %s', (id,))
            conn.commit()
            
            cursor.execute('SELECT * FROM salesorderdetails where maincompanyid = %s', (maincompanyid))
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
                return func.HttpResponse(jsonify({'status': 'salesorderdetails deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)

