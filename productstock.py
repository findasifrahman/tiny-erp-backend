#productstock: productstockid int primary key, maincompanyid int not null unchangeable, purchasecategoryid int not null,
#    purchasesubcategoryid int not null, quantity not null Int, unit not null varchar(15),entrydate timestamp, 
#    status not null varchar(100),description text, 
#    createdat (TIMESTAMP)


from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor
from auth import token_required
import psycopg2
productstock_blueprint = Blueprint('productstock', __name__)


@productstock_blueprint.route('/productstock', methods=['POST'])
@cross_origin()
@token_required
def add_productstock():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO productstock (maincompanyid, productcategoryid, productsubcategoryid, quantity,unit, entrydate, status, description, createdat) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['productcategoryid'], data['productsubcategoryid'], data['quantity'], data['unit'], data['entrydate'], data['status'], data['description'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Product stock added'}), 201

@productstock_blueprint.route('/productstock/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_productstock(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = '''
    SELECT p.*, r.categoryname, s.subcategoryname
    FROM productstock p
    JOIN productcategory r ON p.productcategoryid = r.productcategoryid
    JOIN productsubcategory s ON p.productsubcategoryid = s.productsubcategoryid
    WHERE p.maincompanyid = %s
    '''
    cursor.execute(query, (maincompanyid))
    #cursor.execute('SELECT * FROM productstock where maincompanyid = %s LIMIT 200;', (maincompanyid))
    productstocks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(productstocks), 200

@productstock_blueprint.route('/productstock/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_productstock_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM productstock WHERE productstockid = %s', (id,))
    productstocks = cursor.fetchone()
    cursor.close()
    conn.close()
    if not productstocks:
        return jsonify({'message': 'Product stock not found'}), 404
    return jsonify(productstocks), 200

@productstock_blueprint.route('/productstock/update', methods=['POST'])
@cross_origin()
@token_required
def update_productstock():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE productstock SET  productcategoryid = %s, productsubcategoryid = %s, quantity = %s, unit = %s, entrydate = %s, status = %s, description = %s 
           WHERE productstockid = %s''',
        ( data['productcategoryid'], data['productsubcategoryid'], data['quantity'], data['unit'], data['entrydate'], data['status'], data['description'], data["id"])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Product stock updated'}), 200

@productstock_blueprint.route('/productstock/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_productstock(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    error = False
    try:
        cursor.execute('DELETE FROM productstock WHERE productstockid = %s', (id,))
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
            return jsonify({'status': 'Product stock deleted'}), 200