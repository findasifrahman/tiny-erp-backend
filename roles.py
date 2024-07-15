from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2
from mapp import create_app
import azure.functions as func

roles_blueprint = func.Blueprint('roles', __name__)
app = create_app()#Flask(__name__)

@roles_blueprint.route('roles', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def add_role(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO roles (maincompanyid, rolename, rolepriviledge) VALUES (%s, %s, %s)',
            (data['maincompanyid'], data['rolename'], data['rolepriviledge'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Roles added'}).get_data(as_text=True), mimetype="application/json", status_code=201)

@roles_blueprint.route('roles/{maincompanyid}', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_roles(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM roles where maincompanyid = %s', (maincompanyid))
        roles = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(roles).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@roles_blueprint.route('roles-getbyid', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_role_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM roles WHERE roleid = %s', (id,))
        role = cursor.fetchone()
        cursor.close()
        conn.close()
        response_data = jsonify(role).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@roles_blueprint.route('roles-update', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def update_role(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE roles SET maincompanyid = %s, rolename = %s, rolepriviledge = %s WHERE roleid = %s',
            (data['maincompanyid'], data['rolename'], data['rolepriviledge'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Role updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@roles_blueprint.route('roles', methods=['DELETE'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def delete_role(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():

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
            return func.HttpResponse(jsonify({'message': str(e)}).get_data(as_text=True), mimetype="application/json", status_code=400)

        finally:
            cursor.close()
            conn.close()

        return func.HttpResponse(jsonify({'status': 'Roles deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)
