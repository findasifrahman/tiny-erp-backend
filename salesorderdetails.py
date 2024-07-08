#salesorderdetails: (salesorderdetailid serial primary key, maincompanyid int not null unchangeable), salesorderid INT NOT NULL, productcategoryid INT NOT NULL, 
#productcategoryname varchar(256) not null, productsubcategoryid INT not null, productsubcategoryname varchar(256) not null,  quantity INT NOT NULL, unit VARCHAR(12) not null, 
#unitprice DECIMAL(10, 2) NOT NULL, totaldetailprice DECIMAL(10, 2) NOT NULL, description TEXT createdat TIMESTAMP

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from auth import token_required
from dbcon import get_db_connection

salesorderdetails_blueprint = Blueprint('salesorderdetails', __name__)

@salesorderdetails_blueprint.route('/salesorderdetails', methods=['POST'])
@cross_origin()
@token_required
def add_salesorderdetail():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO salesorderdetails (maincompanyid, salesorderid, productcategoryid, productcategoryname, productsubcategoryid, productsubcategoryname, quantity, unit, unitprice, totaldetailprice, description, createdat) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['salesorderid'], data['productcategoryid'], data['productcategoryname'], data['productsubcategoryid'], data['productsubcategoryname'], data['quantity'], data['unit'], data['unitprice'], data['totaldetailprice'], data['description'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Sales Order Detail added'}), 201

@salesorderdetails_blueprint.route('/salesorderdetails/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_salesorderdetails(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM salesorderdetails where maincompanyid = %s', (maincompanyid))
    salesorderdetails = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(salesorderdetails), 200

@salesorderdetails_blueprint.route('/salesorderdetails/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_salesorderdetail_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM salesorderdetails WHERE salesorderdetailid = %s', (id,))
    salesorderdetail = cursor.fetchone()
    cursor.close()
    conn.close()
    if not salesorderdetail:
        return jsonify({'message': 'Sales Order Detail not found'}), 404
    return jsonify(salesorderdetail), 200

@salesorderdetails_blueprint.route('/salesorderdetails/update', methods=['POST'])
@cross_origin()
@token_required
def update_salesorderdetail():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE salesorderdetails SET salesorderid = %s, productcategoryid = %s, productcategoryname = %s, productsubcategoryid = %s, productsubcategoryname = %s, quantity = %s, unit = %s, unitprice = %s, totaldetailprice = %s, description = %s
           WHERE salesorderdetailid = %s''',
        (data['salesorderid'], data['productcategoryid'], data['productcategoryname'], data['productsubcategoryid'], data['productsubcategoryname'], data['quantity'], data['unit'], data['unitprice'], data['totaldetailprice'], data['description'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Sales Order Detail updated'}), 200

@salesorderdetails_blueprint.route('/salesorderdetails/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_salesorderdetail(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM salesorderdetails WHERE salesorderdetailid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Sales Order Detail deleted'}), 200
