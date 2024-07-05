# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from users import user_blueprint
from maincompany import maincompany_blueprint
from roles import roles_blueprint
from customer import customer_blueprint
from auth import generate_token, token_required
import os
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register blueprints
app.register_blueprint(user_blueprint)
app.register_blueprint(maincompany_blueprint)
app.register_blueprint(roles_blueprint)
app.register_blueprint(customer_blueprint )


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )
    return conn

# Dummy user data for authentication
users = {
    "user1": "password1",
    "user2": "password2"
}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    print(username)
    print(password)

    query = f'''
    SELECT u.*, r.rolename,m.companyname
    FROM users u
    JOIN roles r ON u.roleid = r.roleid
    JOIN maincompany m ON u.maincompanyid = m.maincompanyid
    WHERE u.username = %s AND u.password = %s
    '''
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query,(username, password))#('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
    user = cursor.fetchone()
    print("login user--",user)
    cursor.close()
    conn.close()

    if user:
        token = generate_token(user['username'], user['rolename'])
        print("generated token--",token)
        print(user)
        return jsonify({'token': token, "maincompanyid": user['maincompanyid'], "maincompanyname": user['companyname'] }), 200
    return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
