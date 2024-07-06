#purchasecategory: purchasecategoryid primary key Serial, maincompanyid int not null unchangeable, itemname varchar(128) not null, description TEXT,createdat timestamp


from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor

from auth import token_required

purchasecategory_blueprint = Blueprint('purchasecategory', __name__)


@purchasecategory_blueprint.route('/purchasecategory', methods=['POST'])
@cross_origin()
@token_required
def add_purchasecategory():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO purchasecategory (maincompanyid, itemname, description, createdat) 
           VALUES (%s, %s, %s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['itemname'], data['description'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Purchase Category added'}), 201

@purchasecategory_blueprint.route('/purchasecategory/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_purchasecategories(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM purchasecategory where maincompanyid = %s', (maincompanyid))
    purchasecategories = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(purchasecategories), 200

@purchasecategory_blueprint.route('/purchasecategory/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_purchasecategory_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM purchasecategory WHERE purchasecategoryid = %s', (id,))
    purchasecategory = cursor.fetchone()
    cursor.close()
    conn.close()
    if not purchasecategory:
        return jsonify({'message': 'Purchase Category not found'}), 404
    return jsonify(purchasecategory), 200

@purchasecategory_blueprint.route('/purchasecategory/update', methods=['POST'])
@cross_origin()
@token_required
def update_purchasecategory():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE purchasecategory SET itemname = %s, description = %s 
           WHERE purchasecategoryid = %s''',
        (data['itemname'], data['description'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Purchase Category updated'}), 200

@purchasecategory_blueprint.route('/purchasecategory/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_purchasecategory( id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM purchasecategory WHERE purchasecategoryid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Purchase Category deleted'}), 200
