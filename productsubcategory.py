#productsubcategory: productsubcategoryid SERIAL PRIMARY KEY, maincompanyid int not null unchangeable, productcategoryid int not null,
# categoryname varchar(256) not null,
#subcategoryname varchar(256) not null,  createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required

customer_blueprint = Blueprint('customer', __name__)


@customer_blueprint.route('/productsubcategory', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def add_productsubcategory():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO productsubcategory (maincompanyid,productcategoryid,categoryname,subcategoryname, createdat) VALUES (%s, %s,%s,%s, CURRENT_TIMESTAMP)',
        (data['maincompanyid'], data['productcategoryid'], data['categoryname'], data['subcategoryname'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Product Sub Category added'}), 201

@customer_blueprint.route('/productsubcategory/<maincompanyid>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_productsubcategory(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM productsubcategory where maincompanyid = %s', (maincompanyid))
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users), 200

@customer_blueprint.route('/productsubcategory/getbyid', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_productsubcategory_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM productsubcategory WHERE productsubcategoryid = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user), 200

@customer_blueprint.route('/productsubcategory/update', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def update_productsubcategory():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE productsubcategory SET maincompanyid = %s,productcategoryid = %s, categoryname = %s, subcategoryname = %s WHERE productsubcategoryid = %s',
        (data['maincompanyid'],data['productcategoryid'], data['categoryname'],data['subcategoryname'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Product Sub Category updated'}), 200

@customer_blueprint.route('/productsubcategory/<int:id>', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
@token_required
def delete_productsubcategory(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productsubcategory WHERE productsubcategoryid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Product Sub Category deleted'}), 200
