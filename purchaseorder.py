#purchaseorder: purchaseid serial Primary key, maincompanyid int not null unchangeable, supplierid not null INT, 
#totalamount double not null, purchasedby not null varchar(128),date timestamp, createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from auth import token_required
from dbcon import get_db_connection

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
    cursor.execute('SELECT * FROM purchaseorder where maincompanyid = %s', (maincompanyid))
    purchaseorders = cursor.fetchall()
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
    cursor.execute('DELETE FROM purchaseorder WHERE purchaseid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Purchase Order deleted'}), 200
