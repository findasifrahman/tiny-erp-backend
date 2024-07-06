#paymentsales: paymentid SERIAL PRIMARY KEY, maincompanyid int not null unchangeable, customerid INT NOT NULL, paymentdate DATE NOT NULL, 
#amount DECIMAL(10, 2) NOT NULL,receivedby varchar(256) not null, createdat TIMESTAMP

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required

paymentsales_blueprint = Blueprint('paymentsales', __name__)


@paymentsales_blueprint.route('/paymentsales', methods=['POST'])
@cross_origin()
@token_required
def add_paymentsales():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO paymentsales (maincompanyid, customerid, paymentdate, amount, receivedby, createdat) 
           VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['customerid'], data['paymentdate'], data['amount'], data['receivedby'])
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
def update_paymentsales( id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE paymentsales SET customerid = %s, paymentdate = %s, amount = %s, receivedby = %s 
           WHERE paymentid = %s''',
        (data['customerid'], data['paymentdate'], data['amount'], data['receivedby'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Payment Sales updated'}), 200

@paymentsales_blueprint.route('/paymentsales/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_paymentsales(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM paymentsales WHERE paymentid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Payment Sales deleted'}), 200
