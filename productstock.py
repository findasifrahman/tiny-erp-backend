#productstock: productstockid int primary key, maincompanyid int not null unchangeable, productcategoryid int not null,
#    productsubcategoryid int not null, quantity not null Int, unit not null varchar(15),entrydate timestamp, 
#    status not null varchar(100),description text, 
#    createdat (TIMESTAMP)


from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor
from auth import token_required
import psycopg2
import logging
import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
productstock_blueprint = func.Blueprint('productstock', __name__)


@productstock_blueprint.route('productstock', methods=['POST'])
#@cross_origin()
#@token_required
def add_productstock(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO productstock (maincompanyid, productcategoryid, productsubcategoryid, quantity,unit, entrydate, status, description, createdat) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
            (data['maincompanyid'], data['productcategoryid'], data['productsubcategoryid'], data['quantity'], data['unit'], data['entrydate'], data['status'], data['description'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Product stock added'}).get_data(as_text=True), mimetype="application/json", status_code=201)


@productstock_blueprint.route('productstock/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_productstock(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = '''
        SELECT p.*, r.categoryname, s.subcategoryname
        FROM productstock p
        JOIN productcategory r ON p.productcategoryid = r.productcategoryid
        JOIN productsubcategory s ON p.productsubcategoryid = s.productsubcategoryid
        WHERE p.maincompanyid = %s AND p.entrydate >= NOW() - INTERVAL '3 MONTHS'
        '''
        cursor.execute(query, (maincompanyid))
        #cursor.execute('SELECT * FROM productstock where maincompanyid = %s LIMIT 200;', (maincompanyid))
        productstocks = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(productstocks).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@productstock_blueprint.route('productstock-getall/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_productstock_All(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = '''
        SELECT p.*, r.categoryname, s.subcategoryname
        FROM productstock p
        JOIN productcategory r ON p.productcategoryid = r.productcategoryid
        JOIN productsubcategory s ON p.productsubcategoryid = s.productsubcategoryid
        WHERE p.maincompanyid = %s
        '''
        cursor.execute(query, (maincompanyid))
        #cursor.execute('SELECT * FROM productstock where maincompanyid = %s LIMIT 200;', (maincompanyid))
        productstocks = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(productstocks).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@productstock_blueprint.route('productstock-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_productstock_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM productstock WHERE productstockid = %s', (id,))
        productstocks = cursor.fetchone()
        cursor.close()
        conn.close()
        if not productstocks:
            return func.HttpResponse(jsonify({'status': 'Product stock  found'}).get_data(as_text=True), mimetype="application/json", status_code=404)

        response_data = jsonify(productstocks).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@productstock_blueprint.route('productstock-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_productstock(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE productstock SET  productcategoryid = %s, productsubcategoryid = %s, quantity = %s, unit = %s, entrydate = %s, status = %s, description = %s 
            WHERE productstockid = %s''',
            ( data['productcategoryid'], data['productsubcategoryid'], data['quantity'], data['unit'], data['entrydate'], data['status'], data['description'], data["id"])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Product stock updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@productstock_blueprint.route('productstock', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_productstock(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM productstock WHERE productstockid = %s', (id,))
            conn.commit()
            
            query = '''
            SELECT p.*, r.categoryname, s.subcategoryname
            FROM productstock p
            JOIN productcategory r ON p.productcategoryid = r.productcategoryid
            JOIN productsubcategory s ON p.productsubcategoryid = s.productsubcategoryid
            WHERE p.maincompanyid = %s AND p.entrydate >= NOW() - INTERVAL '3 MONTHS'
            '''
            cursor.execute(query, (maincompanyid))
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
                return func.HttpResponse(jsonify({'status': 'productstock deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)

@productstock_blueprint.route('productstock-getstock', methods=['GET'])
#@cross_origin()
#@token_required
def getstock_productstock(req: func.HttpRequest):
    maincompanyid = req.params.get('maincompanyid')
    categoryid = req.params.get('categoryid')#request.args.get('id')
    subcategoryid = req.params.get('subcategoryid')

    logging.info(f'users_dispatcher is --------------------------- {req.params.get("maincompanyid")} ')
    query = """
    SELECT
        (COALESCE(ps.total_stock, 0) - COALESCE(sod.total_sold, 0)) AS current_stock
    FROM
        (SELECT SUM(quantity) AS total_stock
        FROM productstock
        WHERE maincompanyid = %s
        AND productcategoryid = %s
        AND productsubcategoryid = %s) ps
    LEFT JOIN
        (SELECT SUM(quantity) AS total_sold
        FROM salesorderdetails
        WHERE maincompanyid = %s
        AND productcategoryid = %s
        AND productsubcategoryid = %s) sod
    ON TRUE;


    """


    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()#cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute(query, (maincompanyid, categoryid, subcategoryid,maincompanyid, categoryid, subcategoryid))
            row = cursor.fetchone()
            logging.info(f'result is is --------------------------- {row[0]} ')

        except psycopg2.Error as e:
            error =True
            conn.rollback()
            print("error test is --",e)
            return func.HttpResponse(jsonify({'message': str(e)}).get_data(as_text=True), mimetype="application/json", status_code=400)

        finally:
            cursor.close()
            conn.close()
            # Convert the result to a list of dictionaries
            if row is None:
                return func.HttpResponse(jsonify({'error': 'No data found for the specified parameters'}).get_data(as_text=True), mimetype="application/json", status_code=400)

            current_stock = row[0]

            if not error:
                return func.HttpResponse(jsonify({'status': 'Stock Found', 'data': current_stock}).get_data(as_text=True), mimetype="application/json", status_code=200)
