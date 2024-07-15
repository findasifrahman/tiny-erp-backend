#purchasecategory: purchasecategoryid primary key Serial, maincompanyid int not null unchangeable, itemname varchar(128) not null, description TEXT,createdat timestamp


from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor
import psycopg2
from auth import token_required

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
purchasecategory_blueprint = func.Blueprint('purchasecategory', __name__)


@purchasecategory_blueprint.route('purchasecategory', methods=['POST'])
#@cross_origin()
#@token_required
def add_purchasecategory(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
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
        return func.HttpResponse(jsonify({'status': 'Purchase Category added'}).get_data(as_text=True), mimetype="application/json", status_code=201)


@purchasecategory_blueprint.route('purchasecategory/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_purchasecategories(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM purchasecategory where maincompanyid = %s', (maincompanyid))
        purchasecategories = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(purchasecategories).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@purchasecategory_blueprint.route('purchasecategory-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_purchasecategory_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM purchasecategory WHERE purchasecategoryid = %s', (id,))
        purchasecategory = cursor.fetchone()
        cursor.close()
        conn.close()
        if not purchasecategory:
            return func.HttpResponse(jsonify({'status': 'Purchase Category not found'}).get_data(as_text=True), mimetype="application/json", status_code=404)

        response_data = jsonify(purchasecategory).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@purchasecategory_blueprint.route('purchasecategory-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_purchasecategory(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
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
        #return jsonify({'status': 'Purchase Category updated'}), 200
        return func.HttpResponse(jsonify({'status': 'Purchase Category updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@purchasecategory_blueprint.route('purchasecategory', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_purchasecategory(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM purchasecategory WHERE purchasecategoryid = %s', (id,))
            conn.commit()
            
            cursor.execute('SELECT * FROM purchasecategory where maincompanyid = %s', (maincompanyid))
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
                  return func.HttpResponse(jsonify({'status': 'purchasecategory deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)
