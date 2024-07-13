from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2

import azure.functions as func
roles_blueprint = func.Blueprint('roles', __name__)

@roles_blueprint.route('/roles', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def add_role():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO roles (maincompanyid, rolename, rolepriviledge) VALUES (%s, %s, %s)',
        (data['maincompanyid'], data['rolename'], data['rolepriviledge'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Role added'}), 201

@roles_blueprint.route('/roles/<maincompanyid>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_roles(maincompanyid):
    #maincompanyid = request.args.get('maincompanyid')
    #if not maincompanyid:
    #return jsonify({'message': 'MainCompanyID is required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM roles where maincompanyid = %s', (maincompanyid))
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(roles), 200

@roles_blueprint.route('/roles/getbyid', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_role_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM roles WHERE roleid = %s', (id,))
    role = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(role), 200

@roles_blueprint.route('/roles/update', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def update_role():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE roles SET maincompanyid = %s, rolename = %s, rolepriviledge = %s WHERE roleid = %s',
        (data['maincompanyid'], data['rolename'], data['rolepriviledge'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Role updated'}), 200

@roles_blueprint.route('/roles', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
@token_required
def delete_role():
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Delete the specified sales order detail
        cursor.execute('DELETE FROM roles WHERE roleid = %s', (id,))
        conn.commit()

        # Fetch the updated list of sales order details
        cursor.execute('SELECT * FROM roles where maincompanyid = %s', (maincompanyid))
        roles = cursor.fetchall()

    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'message': str(e)}), 400

    finally:
        cursor.close()
        conn.close()

    return jsonify({'status': 'Sales Order Detail deleted', 'data': roles}), 200
