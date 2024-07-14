#purchaseorderdetails: purchasedetailid serial primary key, maincompanyid int not null unchangeable, purchaseid INT NOT NULL, purchasecategoryid INT not null, 
#categoryname varchar(256) not null, purchasesubcategoryid INT not null, subcategoryname varchar(256) not null, purchaseamount int not null, purchasequantity int not null,  
#unit varchar(15) NOT NULL ,totalamount numeric not null, createdat (TIMESTAMP)


from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
purchaseorderdetail_blueprint = func.Blueprint('purchaseorderdetail', __name__)


@purchaseorderdetail_blueprint.route('/purchaseorderdetail', methods=['POST'])
@cross_origin()
@token_required
def add_purchaseorderdetail():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO purchaseorderdetails (maincompanyid, purchaseid, purchasecategoryid, categoryname, purchasesubcategoryid, subcategoryname, purchaseamount, purchasequantity, unit, totalamount, createdat) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['purchaseid'], data['purchasecategoryid'], data['categoryname'], data['purchasesubcategoryid'], data['subcategoryname'], data['purchaseamount'], data['purchasequantity'], data['unit'], data['totalamount'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Purchase Order Detail added'}), 201

@purchaseorderdetail_blueprint.route('/purchaseorderdetail/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_purchaseorderdetails(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM purchaseorderdetails where maincompanyid = %s', (maincompanyid))
    purchaseorderdetails = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(purchaseorderdetails), 200

@purchaseorderdetail_blueprint.route('/purchaseorderdetail/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_purchaseorderdetail_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM purchaseorderdetails WHERE purchasedetailid = %s', (id,))
    purchaseorderdetail = cursor.fetchone()
    cursor.close()
    conn.close()
    if not purchaseorderdetail:
        return jsonify({'message': 'Purchase Order Detail not found'}), 404
    return jsonify(purchaseorderdetail), 200

@purchaseorderdetail_blueprint.route('/purchaseorderdetail/update', methods=['POST'])
@cross_origin()
@token_required
def update_purchaseorderdetail():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE purchaseorderdetails SET purchaseid = %s, purchasecategoryid = %s, categoryname = %s, purchasesubcategoryid = %s, subcategoryname = %s, purchaseamount = %s, purchasequantity = %s, unit = %s, totalamount = %s 
           WHERE purchasedetailid = %s''',
        (data['purchaseid'], data['purchasecategoryid'], data['categoryname'], data['purchasesubcategoryid'], data['subcategoryname'], data['purchaseamount'], data['purchasequantity'], data['unit'], data['totalamount'], data["id"])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Purchase Order Detail updated'}), 200

@purchaseorderdetail_blueprint.route('/purchaseorderdetail', methods=['DELETE'])
@cross_origin()
@token_required
def delete_purchaseorderdetail():
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    error = False
    try:
        cursor.execute('DELETE FROM purchaseorderdetails WHERE purchasedetailid = %s', (id,))
        conn.commit()
        
        cursor.execute('SELECT * FROM purchaseorderdetails where maincompanyid = %s', (maincompanyid))
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
            return jsonify({'status': 'purchaseorderdetails deleted', 'data': roles}), 200