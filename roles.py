from flask import Blueprint, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

roles_blueprint = Blueprint('roles', __name__)

load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )
    return conn

@roles_blueprint.route('/roles', methods=['POST'])
def add_role():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO roles (MainCompanyID, RoleName, RolePriviledge) VALUES (%s, %s, %s)',
        (data['MainCompanyID'], data['RoleName'], data['RolePriviledge'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Role added'}), 201

@roles_blueprint.route('/roles', methods=['GET'])
def get_roles():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM roles')
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(roles), 200

@roles_blueprint.route('/roles/<int:id>', methods=['GET'])
def get_role_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM roles WHERE RoleID = %s', (id,))
    role = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(role), 200

@roles_blueprint.route('/roles/<int:id>', methods=['PUT'])
def update_role(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE roles SET MainCompanyID = %s, RoleName = %s, RolePriviledge = %s WHERE RoleID = %s',
        (data['MainCompanyID'], data['RoleName'], data['RolePriviledge'], id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Role updated'}), 200

@roles_blueprint.route('/roles/<int:id>', methods=['DELETE'])
def delete_role(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM roles WHERE RoleID = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Role deleted'}), 200
