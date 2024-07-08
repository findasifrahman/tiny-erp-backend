#purchaseorder: purchaseid serial Primary key, maincompanyid int not null unchangeable, supplierid not null INT, 
#totalamount double not null, purchasedby not null varchar(128),date timestamp, createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from auth import token_required
from dbcon import get_db_connection
import psycopg2
from datetime import datetime
purchaseorder_blueprint = Blueprint('purchaseorder', __name__)


@purchaseorder_blueprint.route('/purchaseorder', methods=['POST'])
@cross_origin()
@token_required
def add_purchaseorder():
    data = request.json
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
    return jsonify({'status': 'Purchase Order added'}), 201

@purchaseorder_blueprint.route('/purchaseorder/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_purchaseorders(maincompanyid):
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
    return jsonify(purchaseorders), 200

@purchaseorder_blueprint.route('/purchaseorder/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_purchaseorder_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM purchaseorder WHERE purchaseid = %s', (id,))
    purchaseorder = cursor.fetchone()
    cursor.close()
    conn.close()
    if not purchaseorder:
        return jsonify({'message': 'Purchase Order not found'}), 404
    return jsonify(purchaseorder), 200

@purchaseorder_blueprint.route('/purchaseorder/update', methods=['POST'])
@cross_origin()
@token_required
def update_purchaseorder():
    data = request.json
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
    return jsonify({'status': 'Purchase Order updated'}), 200

@purchaseorder_blueprint.route('/purchaseorder/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_purchaseorder(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    error = False
    try:
        cursor.execute('DELETE FROM purchaseorder WHERE purchaseid = %s', (id,))
        conn.commit()
    except psycopg2.Error as e:
        error =True
        conn.rollback()
        print("error test is --",e)
        return jsonify({'message': str(e)}), 400
    finally:
        cursor.close()
        conn.close()
        if not error:
            return jsonify({'status': 'Purchase Order deleted'}), 200
        

@purchaseorder_blueprint.route('/purchaseorder/getbydate', methods=['GET'])
@cross_origin()  # Enable CORS for this route
def getByDate_purchaseorders():
    id = request.args.get('id')
    dated = request.args.get('dated')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("dated--",dated)
    print("maincompanyid--",id)
    #cursor.execute('SELECT * FROM salesorder WHERE orderdate BETWEEN %s AND %s', (id,))
    cursor.execute('SELECT * FROM purchaseorder WHERE maincompanyid = %s AND date > %s', (id, datetime.strptime(dated, '%Y-%m-%d').date()))
    user = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(user), 200
