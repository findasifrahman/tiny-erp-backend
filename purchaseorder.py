#purchaseorder: purchaseid serial Primary key, maincompanyid int not null unchangeable, supplierid not null INT, 
#totalamount double not null, purchasedby not null varchar(128),date timestamp, createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from auth import token_required
from dbcon import get_db_connection
import psycopg2
from datetime import datetime

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
purchaseorder_blueprint = func.Blueprint('purchaseorder', __name__)


@purchaseorder_blueprint.route('purchaseorder', methods=['POST'])
#@cross_origin()
#@token_required
def add_purchaseorder(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO purchaseorder (maincompanyid, supplierid, totalamount, purchasedby, date, createdat) 
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
            (data['maincompanyid'], data['supplierid'], data['totalamount'], data['purchasedby'], data['date'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Purchase Order  added'}).get_data(as_text=True), mimetype="application/json", status_code=201)


@purchaseorder_blueprint.route('purchaseorder/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_purchaseorders(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # updated by asif
        ############################
        query = '''
        SELECT 
            p.purchaseid,
            p.supplierid,
            p.totalamount,
            p.purchasedby,
            p.date,
            s.suppliercompany,
            json_agg(
                json_build_object(
                    'categoryname', r.categoryname,
                    'subcategoryname', r.subcategoryname,
                    'purchasequantity', r.purchasequantity,
                    'unit', r.unit,
                    'totalamount', r.totalamount
                )
            ) AS details
        FROM purchaseorder p
        LEFT JOIN purchaseorderdetails r ON p.purchaseid = r.purchaseid
        JOIN supplier s ON p.supplierid = s.supplierid
        WHERE p.maincompanyid = %s AND p.date >= NOW() - INTERVAL '3 MONTHS'
        GROUP BY 
            p.purchaseid,
            p.supplierid,
            p.totalamount,
            p.purchasedby,
            p.date,
            s.suppliercompany
        ORDER BY p.date DESC
        '''
        # ############################
        #cursor.execute('SELECT * FROM purchaseorder where maincompanyid = %s', (maincompanyid))
        cursor.execute(query, (maincompanyid))
        purchaseorders = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(purchaseorders).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@purchaseorder_blueprint.route('purchaseorder-getall/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_purchaseorders_getall(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # updated by asif
        query = '''
        SELECT p.*, r.suppliercompany
        FROM purchaseorder p
        JOIN supplier r ON p.supplierid = r.supplierid
        WHERE p.maincompanyid = %s
        '''
        # ############################
        #cursor.execute('SELECT * FROM purchaseorder where maincompanyid = %s', (maincompanyid))
        cursor.execute(query, (maincompanyid))
        purchaseorders = cursor.fetchall()
        print("purchaseorders--",purchaseorders)
        cursor.close()
        conn.close()
        response_data = jsonify(purchaseorders).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@purchaseorder_blueprint.route('purchaseorder-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_purchaseorder_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM purchaseorder WHERE purchaseid = %s', (id,))
        purchaseorder = cursor.fetchone()
        cursor.close()
        conn.close()
        if not purchaseorder:
            return func.HttpResponse(jsonify({'status': 'Purchase Order not found'}).get_data(as_text=True), mimetype="application/json", status_code=404)

        response_data = jsonify(purchaseorder).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@purchaseorder_blueprint.route('purchaseorder-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_purchaseorder(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE purchaseorder SET supplierid = %s, totalamount = %s, purchasedby = %s, date = %s 
            WHERE purchaseid = %s''',
            (data['supplierid'], data['totalamount'], data['purchasedby'], data['date'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Purchase Order updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)


@purchaseorder_blueprint.route('purchaseorder', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_purchaseorder(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM purchaseorder WHERE purchaseid = %s', (id,))
            conn.commit()

            ############################
            query = '''
            SELECT 
                p.purchaseid,
                p.supplierid,
                p.totalamount,
                p.purchasedby,
                p.date,
                s.suppliercompany,
                json_agg(
                    json_build_object(
                        'categoryname', r.categoryname,
                        'subcategoryname', r.subcategoryname,
                        'purchasequantity', r.purchasequantity,
                        'unit', r.unit,
                        'totalamount', r.totalamount
                    )
                ) AS details
            FROM purchaseorder p
            LEFT JOIN purchaseorderdetails r ON p.purchaseid = r.purchaseid
            JOIN supplier s ON p.supplierid = s.supplierid
            WHERE p.maincompanyid = %s AND p.date >= NOW() - INTERVAL '3 MONTHS'
            GROUP BY 
                p.purchaseid,
                p.supplierid,
                p.totalamount,
                p.purchasedby,
                p.date,
                s.suppliercompany
            ORDER BY p.date DESC
            '''
            # ############################
            #cursor.execute('SELECT * FROM purchaseorder where maincompanyid = %s', (maincompanyid))
            cursor.execute(query, (maincompanyid))
            roles = cursor.fetchall()
        except psycopg2.Error as e:
            error =True
            conn.rollback()
            return func.HttpResponse(jsonify({'message': str(e)}).get_data(as_text=True), mimetype="application/json", status_code=400)
  
        finally:
            cursor.close()
            conn.close()
            if not error:
                return func.HttpResponse(jsonify({'status': 'purchaseorder deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)


@purchaseorder_blueprint.route('purchaseorder-getbydate', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
def getByDate_purchaseorders(req: func.HttpRequest):
    id = req.params.get('id')
    dated = req.params.get('dated')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        #cursor.execute('SELECT * FROM salesorder WHERE orderdate BETWEEN %s AND %s', (id,))
        cursor.execute('SELECT * FROM purchaseorder WHERE maincompanyid = %s AND date > %s', (id, datetime.strptime(dated, '%Y-%m-%d').date()))
        user = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(user).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)
