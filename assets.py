#assets: assetentryid Serial Primary key, maincompanyid int not null unchangeable, assetname varchar(256) not null, description not null TEXT, assetvalue not null INT,
#purchasedate timestamp not null, image bytea, createdat (TIMESTAMP)

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2
assets_blueprint = Blueprint('assets', __name__)


@assets_blueprint.route('/assets', methods=['POST'])
@cross_origin()
@token_required
def add_asset():
    data = request.json
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
    return jsonify({'status': 'Asset added'}), 201

@assets_blueprint.route('/assets/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_assets(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM assets WHERE maincompanyid = %s', (maincompanyid))
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(assets), 200

@assets_blueprint.route('/assets/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_asset_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM assets WHERE assetentryid = %s', (id,))
    asset = cursor.fetchone()
    cursor.close()
    conn.close()
    if not asset:
        return jsonify({'message': 'Asset not found'}), 404
    return jsonify(asset), 200

@assets_blueprint.route('/assets/update', methods=['POST'])
@cross_origin()
@token_required
def update_asset():
    data = request.json
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
    return jsonify({'status': 'Asset updated'}), 200

@assets_blueprint.route('/assets/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_asset(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    error = False
    try:
        cursor.execute('DELETE FROM assets WHERE assetentryid = %s', (id,))
        conn.commit()
    except psycopg2.Error as e:
        error =True
        conn.rollback()
        print("error test is --",e)
        return jsonify({'message': str(e)}), 400
    finally:
        cursor.close()
        conn.close()
        if not error:
            return jsonify({'status': 'Assets deleted'}), 200
