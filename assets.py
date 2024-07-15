#assets: assetentryid Serial Primary key, maincompanyid int not null unchangeable, assetname varchar(256) not null, description not null TEXT, assetvalue not null INT,
#purchasedate timestamp not null, image bytea, createdat (TIMESTAMP)

from flask import request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2
import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
assets_blueprint = func.Blueprint('assets', __name__)


@assets_blueprint.route('assets', methods=['POST'])
#@cross_origin()
#@token_required
def add_asset(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO assets (maincompanyid, assetname, description, assetvalue, purchasedate, image, createdat) 
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
            (data['maincompanyid'], data['assetname'], data['description'], data['assetvalue'], data['purchasedate'], data['image'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Asset added'}).get_data(as_text=True), mimetype="application/json", status_code=201)


@assets_blueprint.route('assets/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_assets(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM assets WHERE maincompanyid  = %s', (maincompanyid))
        assets = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(assets).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)



@assets_blueprint.route('assets-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_asset_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM assets WHERE assetentryid = %s', (id,))
        asset = cursor.fetchone()
        cursor.close()
        conn.close()
        if not asset:
            return func.HttpResponse(jsonify({'status': 'Asset not found'}).get_data(as_text=True), mimetype="application/json", status_code=404)

        response_data = jsonify(asset).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@assets_blueprint.route('assets-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_asset(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE assets SET assetname = %s, description = %s, assetvalue = %s, purchasedate = %s, image = %s 
            WHERE assetentryid = %s''',
            (data['assetname'], data['description'], data['assetvalue'], data['purchasedate'], data['image'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Asset updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)


@assets_blueprint.route('assets', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_asset(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Delete the specified sales order detail
            cursor.execute('DELETE FROM assets WHERE assetentryid = %s', (id,))
            conn.commit()

            # Fetch the updated list of sales order details
            cursor.execute('SELECT * FROM assets where maincompanyid = %s', (maincompanyid))
            roles = cursor.fetchall()

        except psycopg2.Error as e:
            conn.rollback()
            return func.HttpResponse(jsonify({'message': str(e)}).get_data(as_text=True), mimetype="application/json", status_code=400)

        finally:
            cursor.close()
            conn.close()

        return func.HttpResponse(jsonify({'status': 'Assets deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)

