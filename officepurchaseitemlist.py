#officeipurchasetemlist: officeipurchasetemlistid SERIAL PRIMARY KEY, maincompanyid int not null unchangeable, itemname varchar(256) not null, price INT not null, description TEXT,  
#createdat TIMESTAMP

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2
officepurchaseitemlist_blueprint = Blueprint('officepurchaseitemlist', __name__)


@officepurchaseitemlist_blueprint.route('/officepurchaseitemlist', methods=['POST'])
@cross_origin()
@token_required
def add_officepurchaseitemlist():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO officepurchaseitemlist (maincompanyid, itemname, price, description, createdat) 
           VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['itemname'], data['price'], data['description'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Office Purchase Item List added'}), 201

@officepurchaseitemlist_blueprint.route('/officepurchaseitemlist/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_officepurchaseitemlists(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM officepurchaseitemlist where maincompanyid = %s', (maincompanyid,))
    officepurchaseitemlists = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(officepurchaseitemlists), 200

@officepurchaseitemlist_blueprint.route('/officepurchaseitemlist/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_officepurchaseitemlist_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM officepurchaseitemlist WHERE officepurchaseitemlistid = %s', (id,))
    officepurchaseitemlist = cursor.fetchone()
    cursor.close()
    conn.close()
    if not officepurchaseitemlist:
        return jsonify({'message': 'Office Purchase Item List not found'}), 404
    return jsonify(officepurchaseitemlist), 200

@officepurchaseitemlist_blueprint.route('/officepurchaseitemlist/update', methods=['POST'])
@cross_origin()
@token_required
def update_officepurchaseitemlist():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    print("data in update is --",data)
    cursor.execute(
        '''UPDATE officepurchaseitemlist SET itemname = %s, price = %s, description = %s 
           WHERE officepurchaseitemlistid = %s''',
        (data['itemname'], data['price'], data['description'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Office Purchase Item List updated'}), 200

@officepurchaseitemlist_blueprint.route('/officepurchaseitemlist', methods=['DELETE'])
@cross_origin()
@token_required
def delete_officepurchaseitemlist():
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    error = False
    try:
        cursor.execute('DELETE FROM officepurchaseitemlist WHERE officepurchaseitemlistid = %s', (id,))
        conn.commit()
        
        cursor.execute('SELECT * FROM officepurchaseitemlist where maincompanyid = %s', (maincompanyid))
        roles = cursor.fetchall()
    except psycopg2.Error as e:
        error =True
        conn.rollback()
        print("error test is --",e)
        return jsonify({'message': str(e)}), 400
    finally:
        cursor.close()
        conn.close()
        if not error:
            return jsonify({'status': 'officepurchaseitemlist deleted', 'data': roles}), 200