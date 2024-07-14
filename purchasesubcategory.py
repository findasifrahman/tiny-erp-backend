#purchasesubcategory: purchasesubcategoryid primary key serial, maincompanyid int not null unchangeable, purchasecategoryid INT not null,categoryname varchar(128),
# subcategoryname varchar(256) not null, price (double not null),description Text, createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
purchasesubcategory_blueprint = func.Blueprint('purchasesubcategory', __name__)


@purchasesubcategory_blueprint.route('/purchasesubcategory', methods=['POST'])
@cross_origin()
@token_required
def add_purchasesubcategory():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO purchasesubcategory (maincompanyid, purchasecategoryid, categoryname, subcategoryname, price, description, createdat) 
           VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['purchasecategoryid'], data['categoryname'], data['subcategoryname'], data['price'], data['description'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Purchase Subcategory added'}), 201

@purchasesubcategory_blueprint.route('/purchasesubcategory/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_purchasesubcategories(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM purchasesubcategory where maincompanyid = %s', (maincompanyid))
    purchasesubcategories = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(purchasesubcategories), 200

@purchasesubcategory_blueprint.route('/purchasesubcategory/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_purchasesubcategory_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM purchasesubcategory WHERE purchasesubcategoryid = %s', (id,))
    purchasesubcategory = cursor.fetchone()
    cursor.close()
    conn.close()
    if not purchasesubcategory:
        return jsonify({'message': 'Purchase Subcategory not found'}), 404
    return jsonify(purchasesubcategory), 200

@purchasesubcategory_blueprint.route('/purchasesubcategory/update', methods=['POST'])
@cross_origin()
@token_required
def update_purchasesubcategory():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE purchasesubcategory SET purchasecategoryid = %s, categoryname = %s, subcategoryname = %s, price = %s, description = %s 
           WHERE purchasesubcategoryid = %s''',
        (data['purchasecategoryid'], data['categoryname'], data['subcategoryname'], data['price'], data['description'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Purchase Subcategory updated'}), 200

@purchasesubcategory_blueprint.route('/purchasesubcategory', methods=['DELETE'])
@cross_origin()
@token_required
def delete_purchasesubcategory():
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    error = False
    try:
        cursor.execute('DELETE FROM purchasesubcategory WHERE purchasesubcategoryid = %s', (id,))
        conn.commit()
        
        cursor.execute('SELECT * FROM purchasesubcategory where maincompanyid = %s', (maincompanyid))
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
            return jsonify({'status': 'purchasesubcategory deleted', 'data': roles}), 200
