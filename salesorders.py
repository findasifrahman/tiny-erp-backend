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
salesorders_blueprint = func.Blueprint('salesorders', __name__)


@salesorders_blueprint.route('salesorders', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def add_salesorders(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO salesorder (maincompanyid, customerid, customercompany, salestype, salesagentid, salesagent, totalamount, status, orderdate, createdat) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, CURRENT_TIMESTAMP)',
            (data['maincompanyid'], data['customerid'], data['customercompany'], data['salestype'], data['salesagentid'], data['salesagent'], data['totalamount'],data['status'],data['orderdate'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'SalesOrder added'}).get_data(as_text=True), mimetype="application/json", status_code=201)


@salesorders_blueprint.route('salesorders/{maincompanyid}', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_salesorders(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # updated by asif
        query = '''
        SELECT 
            p.salesorderid,
            p.maincompanyid,
            p.customerid,
            p.customercompany,
            p.salestype,
            p.salesagentid,
            p.salesagent,
            p.totalamount,
            p.status,
            p.orderdate,
        
            json_agg(
                json_build_object(
                    'productcategoryname', r.productcategoryname,
                    'productsubcategoryname', r.productsubcategoryname,
                    'quantity', r.quantity,
                    'unit', r.unit,
                    'price', r.totaldetailprice
                )
            ) AS details
        FROM salesorder p
        LEFT JOIN salesorderdetails r ON p.salesorderid = r.salesorderid
        WHERE p.maincompanyid = %s AND p.orderdate >= NOW() - INTERVAL '3 MONTHS'
        GROUP BY 
            p.salesorderid,
            p.maincompanyid,
            p.customerid,
            p.customercompany,
            p.salestype,
            p.salesagentid,
            p.salesagent,
            p.totalamount,
            p.status,
            p.orderdate
        ORDER BY p.orderdate DESC
        '''
        # ############################
        cursor.execute(query, (maincompanyid))
        #cursor.execute('SELECT * FROM salesorder where maincompanyid = %s', (maincompanyid))
        users = cursor.fetchall()
        print("users--",users)
        cursor.close()
        conn.close()
        response_data = jsonify(users).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@salesorders_blueprint.route('salesorders-getall/<maincompanyid>', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_salesorders_getall(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # updated by asif
        query = '''
        SELECT 
            p.salesorderid,
            p.maincompanyid,
            p.customerid,
            p.customercompany,
            p.salestype,
            p.salesagentid,
            p.salesagent,
            p.totalamount,
            p.status,
            p.orderdate,
        
            json_agg(
                json_build_object(
                    'productcategoryname', r.productcategoryname,
                    'productsubcategoryname', r.productsubcategoryname,
                    'quantity', r.quantity,
                    'unit', r.unit,
                    'price', r.totaldetailprice
                )
            ) AS details
        FROM salesorder p
        LEFT JOIN salesorderdetails r ON p.salesorderid = r.salesorderid
        WHERE p.maincompanyid = %s
        GROUP BY 
            p.salesorderid,
            p.maincompanyid,
            p.customerid,
            p.customercompany,
            p.salestype,
            p.salesagentid,
            p.salesagent,
            p.totalamount,
            p.status,
            p.orderdate
        '''
        # ############################
        cursor.execute(query, (maincompanyid))
        #cursor.execute('SELECT * FROM salesorder where maincompanyid = %s', (maincompanyid))
        users = cursor.fetchall()
        print("users--",users)
        cursor.close()
        conn.close()
        response_data = jsonify(users).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@salesorders_blueprint.route('salesorders-getbyid', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_salesorders_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM salesorder WHERE salesorderid = %s', (id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        response_data = jsonify(user).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@salesorders_blueprint.route('salesorders-update', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def update_salesorders(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE salesorder SET maincompanyid = %s, customerid = %s, customercompany = %s, salestype = %s,salesagentid = %s, salesagent = %s, totalamount = %s, status = %s, orderdate= %s WHERE salesorderid = %s',
            (data['maincompanyid'], data['customerid'], data['customercompany'], data['salestype'],data['salesagentid'] ,data['salesagent'], data['totalamount'],data['status'],data['orderdate'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Sales Order updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)


@salesorders_blueprint.route('salesorders', methods=['DELETE'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def delete_salesorders(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM salesorder WHERE salesorderid = %s', (id,))
            conn.commit()
            
            query = '''
            SELECT 
                p.salesorderid,
                p.maincompanyid,
                p.customerid,
                p.customercompany,
                p.salestype,
                p.salesagentid,
                p.salesagent,
                p.totalamount,
                p.status,
                p.orderdate,
            
                json_agg(
                    json_build_object(
                        'productcategoryname', r.productcategoryname,
                        'productsubcategoryname', r.productsubcategoryname,
                        'quantity', r.quantity,
                        'unit', r.unit,
                        'price', r.totaldetailprice
                    )
                ) AS details
            FROM salesorder p
            LEFT JOIN salesorderdetails r ON p.salesorderid = r.salesorderid
            WHERE p.maincompanyid = %s AND p.orderdate >= NOW() - INTERVAL '3 MONTHS'
            GROUP BY 
                p.salesorderid,
                p.maincompanyid,
                p.customerid,
                p.customercompany,
                p.salestype,
                p.salesagentid,
                p.salesagent,
                p.totalamount,
                p.status,
                p.orderdate
            ORDER BY p.orderdate DESC
            '''
            # ############################
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
                return func.HttpResponse(jsonify({'status': 'Sales Order deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)
 
        
@salesorders_blueprint.route('salesorders-getbydate', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
def getByDate_salesorders(req: func.HttpRequest):
    with app.app_context():
        id = req.params.get('id')
        dated = req.params.get('dated')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        #cursor.execute('SELECT * FROM salesorder WHERE orderdate BETWEEN %s AND %s', (id,))
        cursor.execute('SELECT * FROM salesorder WHERE maincompanyid = %s AND orderdate > %s', (id, datetime.strptime(dated, '%Y-%m-%d').date()))
        user = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(user).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)
