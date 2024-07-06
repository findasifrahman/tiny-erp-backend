#purchaseorderdetails: purchasedetailid serial primary key, maincompanyid int not null unchangeable, purchaseid INT NOT NULL, purchasecategoryid INT not null, 
#categoryname varchar(256) not null, purchasesubcategoryid INT not null, subcategoryname varchar(256) not null, purchaseamount int not null, purchasequantity int not null,  
#unit varchar(15) NOT NULL ,totalamount numeric not null, createdat (TIMESTAMP)


from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor
from auth import token_required

purchaseorderdetail_blueprint = Blueprint('purchaseorderdetail', __name__)


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

@purchaseorderdetail_blueprint.route('/purchaseorderdetail/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_purchaseorderdetail(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM purchaseorderdetails WHERE purchasedetailid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Purchase Order Detail deleted'}), 200
