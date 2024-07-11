from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from auth import token_required
import psycopg2
from dbcon import get_db_connection

user_blueprint = Blueprint('users', __name__)




@user_blueprint.route('/users', methods=['POST'])
@cross_origin()  # Enable CORS for this route
def add_user():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (maincompanyid, username, password, roleid, createdat) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)',
        (data['maincompanyid'], data['username'], data['password'], data['roleid'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User added'}), 201

@user_blueprint.route('/users/<maincompanyid>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_users(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users where maincompanyid = %s', (maincompanyid))
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users), 200

@user_blueprint.route('/users/getbyid', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_user_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE userid = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user), 200

@user_blueprint.route('/users/update', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def update_user():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET maincompanyid = %s, username = %s, password = %s, roleid = %s WHERE userid = %s',
        (data['maincompanyid'], data['username'], data['password'], data['roleid'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User updated'}), 200

@user_blueprint.route('/users', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
@token_required
def delete_user():
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    error = False
    try:
        cursor.execute('DELETE FROM users WHERE userid = %s', (id,))
        conn.commit()
        
        cursor.execute('SELECT * FROM users where maincompanyid = %s', (maincompanyid))
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
            return jsonify({'status': 'users deleted', 'data': roles}), 200