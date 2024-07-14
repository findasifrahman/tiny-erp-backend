#supplier: supplierid PRIMARY KEY serial, maincompanyid int not null unchangeable, suppliercompany varchar(256) not null, suppliercontactname varchar(128) not null, 
#suppliercontactnumber varchar(30) not null, supplieraddress not null varchar(56),description text, createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
supplier_blueprint = func.Blueprint('supplier', __name__)


@supplier_blueprint.route('supplier', methods=['POST'])
#@cross_origin()
#@token_required
def add_supplier(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO supplier (maincompanyid, suppliercompany, suppliercontactname, suppliercontactnumber, supplieraddress, description, createdat) 
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
            (data['maincompanyid'], data['suppliercompany'], data['suppliercontactname'], data['suppliercontactnumber'], data['supplieraddress'], data['description'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Supplier added'}).get_data(as_text=True), mimetype="application/json", status_code=201)

@supplier_blueprint.route('supplier/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_suppliers(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM supplier where maincompanyid = %s', (maincompanyid))
        suppliers = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(suppliers).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@supplier_blueprint.route('supplier-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_supplier_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM supplier WHERE supplierid = %s', (id,))
        supplier = cursor.fetchone()
        cursor.close()
        conn.close()
        if not supplier:
            return func.HttpResponse(jsonify({'message': 'Supplier not found'}).get_data(as_text=True), mimetype="application/json", status_code=400)
        response_data = jsonify(supplier).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@supplier_blueprint.route('supplier-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_supplier(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE supplier SET suppliercompany = %s, suppliercontactname = %s, suppliercontactnumber = %s, supplieraddress = %s, description = %s 
            WHERE supplierid = %s''',
            (data['suppliercompany'], data['suppliercontactname'], data['suppliercontactnumber'], data['supplieraddress'], data['description'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Supplier updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@supplier_blueprint.route('supplier', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_supplier(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM supplier WHERE supplierid = %s', (id,))
            conn.commit()
            
            cursor.execute('SELECT * FROM supplier where maincompanyid = %s', (maincompanyid))
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
                return func.HttpResponse(jsonify({'status': 'supplier deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)