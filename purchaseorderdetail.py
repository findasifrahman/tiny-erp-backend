#purchaseorderdetails: purchasedetailid serial primary key, maincompanyid int not null unchangeable, purchaseid INT NOT NULL, purchasecategoryid INT not null, 
#categoryname varchar(256) not null, purchasesubcategoryid INT not null, subcategoryname varchar(256) not null, purchaseamount int not null, purchasequantity int not null,  
#unit varchar(15) NOT NULL ,totalamount numeric not null, createdat (TIMESTAMP)


from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
purchaseorderdetail_blueprint = func.Blueprint('purchaseorderdetail', __name__)


@purchaseorderdetail_blueprint.route('purchaseorderdetail', methods=['POST'])
#@cross_origin()
#@token_required
def add_purchaseorderdetail(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO purchaseorderdetails (maincompanyid, purchaseid, purchasecategoryid, categoryname, purchasesubcategoryid, subcategoryname, purchaseamount, purchasequantity, unit, totalamount, createdat) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
            (data['maincompanyid'], data['purchaseid'], data['purchasecategoryid'], data['categoryname'], data['purchasesubcategoryid'], data['subcategoryname'], data['purchaseamount'], data['purchasequantity'], data['unit'], data['totalamount'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Purchase Order Detail added'}).get_data(as_text=True), mimetype="application/json", status_code=201)

@purchaseorderdetail_blueprint.route('purchaseorderdetail/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_purchaseorderdetails(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM purchaseorderdetails where maincompanyid = %s', (maincompanyid))
        purchaseorderdetails = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(purchaseorderdetails).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@purchaseorderdetail_blueprint.route('purchaseorderdetail-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_purchaseorderdetail_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM purchaseorderdetails WHERE purchasedetailid = %s', (id,))
        purchaseorderdetail = cursor.fetchone()
        cursor.close()
        conn.close()
        if not purchaseorderdetail:
            return func.HttpResponse(jsonify({'message': 'Purchase Order Detail not found'}).get_data(as_text=True), mimetype="application/json", status_code=404)

        response_data = jsonify(purchaseorderdetail).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@purchaseorderdetail_blueprint.route('purchaseorderdetail-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_purchaseorderdetail(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE purchaseorderdetails SET purchaseid = %s, purchasecategoryid = %s, categoryname = %s, purchasesubcategoryid = %s, subcategoryname = %s, purchaseamount = %s, purchasequantity = %s, unit = %s, totalamount = %s 
            WHERE purchasedetailid = %s''',
            (data['purchaseid'], data['purchasecategoryid'], data['categoryname'], data['purchasesubcategoryid'], data['subcategoryname'], data['purchaseamount'], data['purchasequantity'], data['unit'], data['totalamount'], data["id"])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Purchase Order Detail updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@purchaseorderdetail_blueprint.route('purchaseorderdetail', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_purchaseorderdetail(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM purchaseorderdetails WHERE purchasedetailid = %s', (id,))
            conn.commit()
            
            cursor.execute('SELECT * FROM purchaseorderdetails where maincompanyid = %s', (maincompanyid))
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
                return func.HttpResponse(jsonify({'status': 'purchaseorderdetails deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)
