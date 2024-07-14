#productcategory: productcategoryid SERIAL PRIMARY KEY, maincompanyid int not null unchangeable, categoryname varchar(256) not null,  
# createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
productcategory_blueprint = func.Blueprint('productcategory', __name__)


@productcategory_blueprint.route('/productcategory', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def add_productcategory():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO productcategory (maincompanyid, categoryname, createdat) VALUES (%s, %s, CURRENT_TIMESTAMP)',
        (data['maincompanyid'], data['categoryname'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Product Category added'}), 201

@productcategory_blueprint.route('/productcategory/<maincompanyid>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_productcategory(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM productcategory where maincompanyid = %s', (maincompanyid))
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users), 200

@productcategory_blueprint.route('/productcategory/getbyid', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_productcategory_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM productcategory WHERE productcategoryid = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user), 200

@productcategory_blueprint.route('/productcategory/update', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def update_productcategory():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE productcategory SET maincompanyid = %s, categoryname = %s WHERE productcategoryid = %s',
        (data['maincompanyid'], data['categoryname'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Product Category updated'}), 200

@productcategory_blueprint.route('/productcategory', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
@token_required
def delete_productcategory():
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    error = False
    try:
        cursor.execute('DELETE FROM productcategory WHERE productcategoryid = %s', (id,))
        conn.commit()
        
        cursor.execute('SELECT * FROM productcategory where maincompanyid = %s', (maincompanyid))
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
            return jsonify({'status': 'productcategory deleted', 'data': roles}), 200