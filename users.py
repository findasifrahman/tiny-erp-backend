from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from auth import token_required
import psycopg2
from dbcon import get_db_connection
from mapp import create_app
#user_blueprint = func.Blueprint('users', __name__)
import azure.functions as func 

user_blueprint = func.Blueprint() 
app = create_app()#Flask(__name__)


@user_blueprint.route('users', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
def add_user(req: func.HttpRequest):
    with app.app_context():
        #data = request.json
        data = req.get_json()
        print("data is --",data)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (maincompanyid, username, password, roleid, createdat) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)',
            (data['maincompanyid'], data['username'], data['password'], data['roleid'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'User added'}).get_data(as_text=True), mimetype="application/json", status_code=201)

@user_blueprint.route('users/{maincompanyid}', methods=['GET'])
#@token_required
def get_users(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    ##
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM users where maincompanyid = %s', (maincompanyid))
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(users).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@user_blueprint.route('users-getbyid', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
async def get_user_by_id(req: func.HttpRequest):
    with app.app_context():
        id = req.params.get('id')
        print("id is --",id)
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM users WHERE userid = %s', (id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        response_data = jsonify(user).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@user_blueprint.route('users-update', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def update_user(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET maincompanyid = %s, username = %s, password = %s, roleid = %s WHERE userid = %s',
            (data['maincompanyid'], data['username'], data['password'], data['roleid'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'User updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@user_blueprint.route('users', methods=['DELETE'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def delete_user(req: func.HttpRequest):
    with app.app_context():
        id = req.params.get('id')#request.args.get('id')
        maincompanyid = req.params.get('maincompanyid')
        print("id is --",id)
        print("maincompanyid is --",maincompanyid)
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
            return func.HttpResponse(jsonify({'message': str(e)}).get_data(as_text=True), mimetype="application/json", status_code=400)
        finally:
            cursor.close()
            conn.close()
            if not error:
                response_data = jsonify({'data':roles}).get_data(as_text=True)
                return func.HttpResponse(response_data, mimetype="application/json", status_code=200)