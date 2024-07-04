from flask import Blueprint, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

user_blueprint = Blueprint('users', __name__)

load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )
    return conn

@user_blueprint.route('/users', methods=['POST'])
def add_user():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (MainCompanyID, username, password, RoleID, createdAt) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)',
        (data['MainCompanyID'], data['username'], data['password'], data['RoleID'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User added'}), 201

@user_blueprint.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users), 200

@user_blueprint.route('/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE UserID = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user), 200

@user_blueprint.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET MainCompanyID = %s, username = %s, password = %s, RoleID = %s WHERE UserID = %s',
        (data['MainCompanyID'], data['username'], data['password'], data['RoleID'], id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User updated'}), 200

@user_blueprint.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE UserID = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User deleted'}), 200
