#purchasesubcategory: purchasesubcategoryid primary key serial, maincompanyid int not null unchangeable, purchasecategoryid INT not null,categoryname varchar(128),
# subcategoryname varchar(256) not null, price (double not null),description Text, createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
purchasesubcategory_blueprint = func.Blueprint('purchasesubcategory', __name__)


@purchasesubcategory_blueprint.route('purchasesubcategory', methods=['POST'])
#@cross_origin()
#@token_required
def add_purchasesubcategory(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO purchasesubcategory (maincompanyid, purchasecategoryid, categoryname, subcategoryname, price, description, createdat) 
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
            (data['maincompanyid'], data['purchasecategoryid'], data['categoryname'], data['subcategoryname'], data['price'], data['description'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Purchase Subcategory added'}).get_data(as_text=True), mimetype="application/json", status_code=201)

@purchasesubcategory_blueprint.route('purchasesubcategory/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_purchasesubcategories(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM purchasesubcategory where maincompanyid = %s', (maincompanyid))
        purchasesubcategories = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(purchasesubcategories).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@purchasesubcategory_blueprint.route('purchasesubcategory-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_purchasesubcategory_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM purchasesubcategory WHERE purchasesubcategoryid = %s', (id,))
        purchasesubcategory = cursor.fetchone()
        cursor.close()
        conn.close()
        if not purchasesubcategory:
            return func.HttpResponse(jsonify({'status': 'purchasesubcategory found'}).get_data(as_text=True), mimetype="application/json", status_code=404)

        response_data = jsonify(purchasesubcategory).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@purchasesubcategory_blueprint.route('purchasesubcategory-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_purchasesubcategory(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE purchasesubcategory SET purchasecategoryid = %s, categoryname = %s, subcategoryname = %s, price = %s, description = %s 
            WHERE purchasesubcategoryid = %s''',
            (data['purchasecategoryid'], data['categoryname'], data['subcategoryname'], data['price'], data['description'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Purchase Subcategory updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)


@purchasesubcategory_blueprint.route('purchasesubcategory', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_purchasesubcategory(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM purchasesubcategory WHERE purchasesubcategoryid = %s', (id,))
            conn.commit()
            
            cursor.execute('SELECT * FROM purchasesubcategory where maincompanyid = %s', (maincompanyid))
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
                return func.HttpResponse(jsonify({'status': 'purchasesubcategory deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)

