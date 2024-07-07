#supplier: supplierid PRIMARY KEY serial, maincompanyid int not null unchangeable, suppliercompany varchar(256) not null, suppliercontactname varchar(128) not null, 
#suppliercontactnumber varchar(30) not null, supplieraddress not null varchar(56),description text, createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2
supplier_blueprint = Blueprint('supplier', __name__)


@supplier_blueprint.route('/supplier', methods=['POST'])
@cross_origin()
@token_required
def add_supplier():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO supplier (maincompanyid, suppliercompany, suppliercontactname, suppliercontactnumber, supplieraddress, description, createdat) 
           VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['suppliercompany'], data['suppliercontactname'], data['suppliercontactnumber'], data['supplieraddress'], data['description'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Supplier added'}), 201

@supplier_blueprint.route('/supplier/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_suppliers(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM supplier where maincompanyid = %s', (maincompanyid))
    suppliers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(suppliers), 200

@supplier_blueprint.route('/supplier/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_supplier_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM supplier WHERE supplierid = %s', (id,))
    supplier = cursor.fetchone()
    cursor.close()
    conn.close()
    if not supplier:
        return jsonify({'message': 'Supplier not found'}), 404
    return jsonify(supplier), 200

@supplier_blueprint.route('/supplier/update', methods=['POST'])
@cross_origin()
@token_required
def update_supplier():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE supplier SET suppliercompany = %s, suppliercontactname = %s, suppliercontactnumber = %s, supplieraddress = %s, description = %s 
           WHERE supplierid = %s''',
        (data['suppliercompany'], data['suppliercontactname'], data['suppliercontactnumber'], data['supplieraddress'], data['description'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Supplier updated'}), 200

@supplier_blueprint.route('/supplier/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_supplier(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    error = False
    try:
        cursor.execute('DELETE FROM supplier WHERE supplierid = %s', (id,))
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
            return jsonify({'status': 'Supplier deleted'}), 200