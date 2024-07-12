#paymentsales: paymentid SERIAL PRIMARY KEY, maincompanyid int not null unchangeable, customerid INT NOT NULL, paymentdate DATE NOT NULL, 
#amount DECIMAL(10, 2) NOT NULL,receivedby varchar(256) not null, createdat TIMESTAMP

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2
paymentsales_blueprint = Blueprint('paymentsales', __name__)


@paymentsales_blueprint.route('/paymentsales', methods=['POST'])
@cross_origin()
@token_required
def add_paymentsales():
    data = request.json
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
    return jsonify({'status': 'Payment Sales added'}), 201

@paymentsales_blueprint.route('/paymentsales/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_paymentsales(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = '''
    SELECT * FROM paymentsales where maincompanyid = %s AND paymentdate >= NOW() - INTERVAL '3 MONTHS' ORDER BY paymentdate DESC
    '''
    cursor.execute(query, (maincompanyid))
    paymentsales = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(paymentsales), 200

@paymentsales_blueprint.route('/paymentsales/getall/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_paymentsales_all(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM paymentsales where maincompanyid = %s', (maincompanyid))
    paymentsales = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(paymentsales), 200

@paymentsales_blueprint.route('/paymentsales/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_paymentsales_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM paymentsales WHERE paymentid = %s', (id,))
    paymentsales = cursor.fetchone()
    cursor.close()
    conn.close()
    if not paymentsales:
        return jsonify({'message': 'Payment Sales not found'}), 404
    return jsonify(paymentsales), 200

@paymentsales_blueprint.route('/paymentsales/update', methods=['POST'])
@cross_origin()
@token_required
def update_paymentsales():
    data = request.json
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
    return jsonify({'status': 'Payment Sales updated'}), 200

@paymentsales_blueprint.route('/paymentsales', methods=['DELETE'])
@cross_origin()
@token_required
def delete_paymentsales():
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
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
        return jsonify({'message': str(e)}), 400
    finally:
        cursor.close()
        conn.close()
        if not error:
            return jsonify({'status': 'paymentsales deleted', 'data': roles}), 200