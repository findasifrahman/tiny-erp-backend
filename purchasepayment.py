# salesorder:salesorderid serial p_key,maincompanyid int not null,customerid int not null, customercompany varchar(256) not null, 
# salestype varchar(20) not null, salesagent notnull varchar(128), totalamount float,
#status default pending not null varchar(50),orderdate timestamp_without_timezone, createdat timestamp without time zone

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2
from datetime import datetime

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
purchasepayment_blueprint = func.Blueprint('purchasepayment', __name__)


@purchasepayment_blueprint.route('purchasepayment', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def add_purchasepayment(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO purchasepayment (maincompanyid, amount, supplierid, paymentorderid, paymentdate, recievedby, description, createdat) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)',
            (data['maincompanyid'], data['amount'], data['supplierid'], data['paymentorderid'], data['paymentdate'], data['recievedby'], data['description'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'added'}).get_data(as_text=True), mimetype="application/json", status_code=201)


@purchasepayment_blueprint.route('purchasepayment/{maincompanyid}', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_purchasepayment(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # updated by asif
        query = '''
        SELECT 
        p.purchasepaymentid,
        p.maincompanyid,
        p.amount,
        p.supplierid,
        p.paymentorderid,
        p.paymentdate,
        p.recievedby,
        p.description,
        p.createdat,
        json_agg(
            json_build_object(
                'suppliercompany', r.suppliercompany,
                'suppliercontactname', r.suppliercontactname,
                'suppliercontactnumber', r.suppliercontactnumber
            )
        ) AS details
        FROM purchasepayment p
        LEFT JOIN supplier r ON p.supplierid = r.supplierid
        WHERE p.maincompanyid = %s AND p.paymentdate >= NOW() - INTERVAL '6 MONTHS'
        GROUP BY 
            p.purchasepaymentid,
            p.maincompanyid,
            p.amount,
            p.supplierid,
            p.paymentorderid,
            p.paymentdate,
            p.recievedby,
            p.description,
            p.createdat
        ORDER BY p.paymentdate DESC
        '''
        query1 = '''
        SELECT p.*, r.suppliercompany, s.employeename
        FROM purchasepayment p
        JOIN supplier r ON p.supplierid = r.supplierid
        JOIN employee s ON p.recievedby = s.employeeid
        WHERE p.maincompanyid = %s AND p.paymentdate >= NOW() - INTERVAL '6 MONTHS'
        '''
        # ############################
        cursor.execute(query1, (maincompanyid))
        #cursor.execute('SELECT * FROM salesorder where maincompanyid = %s', (maincompanyid))
        users = cursor.fetchall()
        print("users--",users)
        cursor.close()
        conn.close()
        response_data = jsonify(users).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@purchasepayment_blueprint.route('purchasepayment-getall/<maincompanyid>', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_purchasepayment_getall(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # updated by asif
        
        query = '''
        SELECT 
            p.purchasepaymentid,
            p.maincompanyid,
            p.amount,
            p.supplierid,
            p.paymentorderid,
            p.paymentdate,
            p.recievedby,
            p.description,
            p.createdat,
            json_agg(
                json_build_object(
                    'suppliercompany', r.suppliercompany,
                    'suppliercontactname', r.suppliercontactname,
                    'suppliercontactnumber', r.suppliercontactnumber
                )
            ) AS details
        FROM purchasepayment p
        LEFT JOIN supplier r ON p.supplierid = r.supplierid
        WHERE p.maincompanyid = %s AND p.paymentdate >= NOW() - INTERVAL '24 MONTHS'
        GROUP BY 
            p.purchasepaymentid,
            p.maincompanyid,
            p.amount,
            p.supplierid,
            p.paymentorderid,
            p.paymentdate,
            p.recievedby,
            p.description,
            p.createdat
        ORDER BY p.paymentdate DESC
        '''
        query1 = '''
        SELECT p.*, r.suppliercompany, s.employeename
        FROM purchasepayment p
        JOIN supplier r ON p.supplierid = r.supplierid
        JOIN employee s ON p.recievedby = s.employeeid
        WHERE p.maincompanyid = %s AND p.paymentdate >= NOW() - INTERVAL '6 MONTHS'
        '''
        # ############################
        cursor.execute(query1, (maincompanyid))
        #cursor.execute('SELECT * FROM salesorder where maincompanyid = %s', (maincompanyid))
        users = cursor.fetchall()
        #print("users--",users)
        cursor.close()
        conn.close()
        response_data = jsonify(users).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@purchasepayment_blueprint.route('purchasepayment-getbyid', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_purchasepayment_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM purchasepayment WHERE purchasepaymentid = %s', (id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        response_data = jsonify(user).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@purchasepayment_blueprint.route('purchasepayment-update', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def update_purchasepayment(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE purchasepayment SET maincompanyid = %s, amount = %s, supplierid = %s, paymentorderid = %s,paymentdate = %s, recievedby = %s, description = %s WHERE purchasepaymentid = %s',
            (data['maincompanyid'], data['amount'], data['supplierid'], data['paymentorderid'],data['paymentdate'] ,data['recievedby'], data['description'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)


@purchasepayment_blueprint.route('purchasepayment', methods=['DELETE'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def delete_purchasepayment(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM purchasepayment WHERE purchasepaymentid = %s', (id,))
            conn.commit()
            
            query = '''
                SELECT 
                    p.purchasepaymentid,
                    p.maincompanyid,
                    p.amount,
                    p.supplierid,
                    p.paymentorderid,
                    p.paymentdate,
                    p.recievedby,
                    p.description,
                    p.createdat,
                
                    json_agg(
                        json_build_object(
                            'suppliercompany', r.suppliercompany,
                            'suppliercontactname', r.suppliercontactname,
                            'suppliercontactnumber', r.suppliercontactnumber
                        )
                    ) AS details
                FROM purchasepayment p
                LEFT JOIN supplier r ON p.supplierid = r.supplierid
                WHERE p.maincompanyid = %s AND p.paymentdate >= NOW() - INTERVAL '6 MONTHS'
                GROUP BY 
                    p.purchasepaymentid,
                    p.maincompanyid,
                    p.amount,
                    p.supplierid,
                    p.paymentorderid,
                    p.paymentdate,
                    p.recievedby,
                    p.description,
                    p.createdat
                ORDER BY p.paymentdate DESC
                '''
            query1 = '''
            SELECT p.*, r.suppliercompany, s.employeename
            FROM purchasepayment p
            JOIN supplier r ON p.supplierid = r.supplierid
            JOIN employee s ON p.recievedby = s.employeeid
            WHERE p.maincompanyid = %s AND p.paymentdate >= NOW() - INTERVAL '6 MONTHS'
            '''
            # ############################
            cursor.execute(query1, (maincompanyid))
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
                return func.HttpResponse(jsonify({'status': 'Sales Order deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)
 
        
@purchasepayment_blueprint.route('purchasepayment-getbydate', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
def getByDate_purchasepayment(req: func.HttpRequest):
    with app.app_context():
        id = req.params.get('id')
        dated = req.params.get('dated')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        #cursor.execute('SELECT * FROM salesorder WHERE orderdate BETWEEN %s AND %s', (id,))
        cursor.execute('SELECT * FROM purchasepayment WHERE maincompanyid = %s AND paymentdate > %s', (id, datetime.strptime(dated, '%Y-%m-%d').date()))
        user = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(user).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)
