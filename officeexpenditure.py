#officeexpenditure: officeexpenditureid Serial primary key, maincompanyid int not null unchangeable, officepurchaseitemlistid INT not null, price INT NOT null, 
#unit not null varchar(15), quantity INT not null, totalamount INT NOT NULL, description text, createdat (TIMESTAMP), date timestamp 

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor
import psycopg2
from auth import token_required

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
officeexpenditure_blueprint = func.Blueprint('officeexpenditure', __name__)

@officeexpenditure_blueprint.route('/officeexpenditure', methods=['POST'])
@cross_origin()
@token_required
def add_officeexpenditure():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO officeexpenditure (maincompanyid, officepurchaseitemlistid, price, unit, quantity, totalamount, description,date, createdat) 
           VALUES (%s, %s, %s, %s, %s, %s, %s,%s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['officepurchaseitemlistid'], data['price'], data['unit'], data['quantity'], data['totalamount'], data['description'], data['date'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Office Expenditure added'}), 201

@officeexpenditure_blueprint.route('/officeexpenditure/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_officeexpenditures(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    # updated by asif
    query = '''
    SELECT p.*, r.itemname
    FROM officeexpenditure p
    JOIN officepurchaseitemlist r ON p.officepurchaseitemlistid = r.officepurchaseitemlistid
    WHERE p.maincompanyid = %s AND p.date >= NOW() - INTERVAL '3 MONTHS'
    ORDER BY p.date DESC
    '''
    # ############################
    cursor.execute(query, (maincompanyid))
    officeexpenditures = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(officeexpenditures), 200

@officeexpenditure_blueprint.route('/officeexpenditure/getall/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_officeexpenditures_all(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    # updated by asif
    query = '''
    SELECT p.*, r.itemname
    FROM officeexpenditure p
    JOIN officepurchaseitemlist r ON p.officepurchaseitemlistid = r.officepurchaseitemlistid
    WHERE p.maincompanyid = %s
    '''
    # ############################
    cursor.execute(query, (maincompanyid))
    officeexpenditures = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(officeexpenditures), 200



@officeexpenditure_blueprint.route('/officeexpenditure/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_officeexpenditure_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM officeexpenditure WHERE officeexpenditureid = %s', (id,))
    officeexpenditure = cursor.fetchone()
    cursor.close()
    conn.close()
    if not officeexpenditure:
        return jsonify({'message': 'Office Expenditure not found'}), 404
    return jsonify(officeexpenditure), 200

@officeexpenditure_blueprint.route('/officeexpenditure/update', methods=['POST'])
@cross_origin()
@token_required
def update_officeexpenditure():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE officeexpenditure SET officepurchaseitemlistid = %s, price = %s, unit = %s, quantity = %s, totalamount = %s, description = %s, date = %s 
           WHERE officeexpenditureid = %s''',
        (data['officepurchaseitemlistid'], data['price'], data['unit'], data['quantity'], data['totalamount'], data['description'],data['date'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Office Expenditure updated'}), 200

@officeexpenditure_blueprint.route('/officeexpenditure', methods=['DELETE'])
@cross_origin()
@token_required
def delete_officeexpenditure():        
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    error = False
    try:
        cursor.execute('DELETE FROM officeexpenditure WHERE officeexpenditureid = %s', (id,))
        conn.commit()
        query = '''
        SELECT p.*, r.itemname
        FROM officeexpenditure p
        JOIN officepurchaseitemlist r ON p.officepurchaseitemlistid = r.officepurchaseitemlistid
        WHERE p.maincompanyid = %s AND p.date >= NOW() - INTERVAL '3 MONTHS'
        ORDER BY p.date DESC
        '''
        # ############################
        cursor.execute(query, (maincompanyid))
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
            return jsonify({'status': 'officeexpenditure deleted', 'data': roles}), 200
