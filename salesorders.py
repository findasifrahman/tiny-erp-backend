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
salesorders_blueprint = Blueprint('salesorders', __name__)


@salesorders_blueprint.route('/salesorders', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def add_salesorders():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO salesorder (maincompanyid, customerid, customercompany, salestype, salesagentid, salesagent, totalamount, status, orderdate, createdat) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, CURRENT_TIMESTAMP)',
        (data['maincompanyid'], data['customerid'], data['customercompany'], data['salestype'], data['salesagentid'], data['salesagent'], data['totalamount'],data['status'],data['orderdate'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Salesorder added'}), 201

@salesorders_blueprint.route('/salesorders/<maincompanyid>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_salesorders(maincompanyid):
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
    return jsonify(users), 200

@salesorders_blueprint.route('/salesorders/getall/<maincompanyid>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_salesorders_getall(maincompanyid):
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
    return jsonify(users), 200

@salesorders_blueprint.route('/salesorders/getbyid', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_salesorders_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM salesorder WHERE salesorderid = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user), 200

@salesorders_blueprint.route('/salesorders/update', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def update_salesorders():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE salesorder SET maincompanyid = %s, customerid = %s, customercompany = %s, salestype = %s,salesagentid = %s, salesagent = %s, totalamount = %s, status = %s, orderdate= %s WHERE salesorderid = %s',
        (data['maincompanyid'], data['customerid'], data['customercompany'], data['salestype'],data['salesagentid'] ,data['salesagent'], data['totalamount'],data['status'],data['orderdate'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Sales Order updated'}), 200

@salesorders_blueprint.route('/salesorders', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
@token_required
def delete_salesorders():
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
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
        return jsonify({'message': str(e)}), 400
    finally:
        cursor.close()
        conn.close()
        if not error:
            return jsonify({'status': 'salesorder deleted', 'data': roles}), 200
        
@salesorders_blueprint.route('/salesorders/getbydate', methods=['GET'])
@cross_origin()  # Enable CORS for this route
def getByDate_salesorders():
    id = request.args.get('id')
    dated = request.args.get('dated')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("dated--",dated)
    print("maincompanyid--",id)
    #cursor.execute('SELECT * FROM salesorder WHERE orderdate BETWEEN %s AND %s', (id,))
    cursor.execute('SELECT * FROM salesorder WHERE maincompanyid = %s AND orderdate > %s', (id, datetime.strptime(dated, '%Y-%m-%d').date()))
    user = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(user), 200