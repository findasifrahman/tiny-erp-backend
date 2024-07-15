#productsubcategory: productsubcategoryid SERIAL PRIMARY KEY, maincompanyid int not null unchangeable, productcategoryid int not null,
# categoryname varchar(256) not null,
#subcategoryname varchar(256) not null,  createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
productsubcategory_blueprint = func.Blueprint('productsubcategory', __name__)


@productsubcategory_blueprint.route('productsubcategory', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def add_productsubcategory(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO productsubcategory (maincompanyid,productcategoryid,categoryname,subcategoryname,price, createdat) VALUES (%s, %s,%s,%s,%s, CURRENT_TIMESTAMP)',
            (data['maincompanyid'], data['productcategoryid'], data['categoryname'], data['subcategoryname'], data['price'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Product Sub Category added'}).get_data(as_text=True), mimetype="application/json", status_code=201)

@productsubcategory_blueprint.route('productsubcategory/{maincompanyid}', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_productsubcategory(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM productsubcategory where maincompanyid = %s', (maincompanyid))
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(users).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@productsubcategory_blueprint.route('productsubcategory-getbyid', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_productsubcategory_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM productsubcategory WHERE productsubcategoryid = %s', (id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        response_data = jsonify(user).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@productsubcategory_blueprint.route('productsubcategory-update', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def update_productsubcategory(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE productsubcategory SET maincompanyid = %s,productcategoryid = %s, categoryname = %s, subcategoryname = %s,price = %s WHERE productsubcategoryid = %s',
            (data['maincompanyid'],data['productcategoryid'], data['categoryname'],data['subcategoryname'], data['price'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Product Sub Category updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@productsubcategory_blueprint.route('productsubcategory', methods=['DELETE'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def delete_productsubcategory(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM productsubcategory WHERE productsubcategoryid = %s', (id,))
            conn.commit()
            
            cursor.execute('SELECT * FROM productsubcategory where maincompanyid = %s', (maincompanyid))
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
                return func.HttpResponse(jsonify({'status': 'productsubcategory deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)
