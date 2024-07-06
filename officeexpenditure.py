#officeexpenditure: officeexpenditureid Serial primary key, maincompanyid int not null unchangeable, officeipurchasetemlistid INT not null, price INT null, unit not 
#null varchar(15), quantity INT not null, totalamount INT NOT NULL, description text, createdat (TIMESTAMP) 
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from dbcon import get_db_connection
from psycopg2.extras import RealDictCursor

from auth import token_required

officeexpenditure_blueprint = Blueprint('officeexpenditure', __name__)

@officeexpenditure_blueprint.route('/officeexpenditure', methods=['POST'])
@cross_origin()
@token_required
def add_officeexpenditure(user_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO officeexpenditure (maincompanyid, officeipurchasetemlistid, price, unit, quantity, totalamount, description,date, createdat) 
           VALUES (%s, %s, %s, %s, %s, %s, %s,%s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['officeipurchasetemlistid'], data['price'], data['unit'], data['quantity'], data['totalamount'], data['description'], data['date'])
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
    cursor.execute('SELECT * FROM officeexpenditure where maincompanyid = %s', (maincompanyid))
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
        '''UPDATE officeexpenditure SET officeipurchasetemlistid = %s, price = %s, unit = %s, quantity = %s, totalamount = %s, description = %s, date = %s 
           WHERE officeexpenditureid = %s''',
        (data['officeipurchasetemlistid'], data['price'], data['unit'], data['quantity'], data['totalamount'], data['description'],data['date'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Office Expenditure updated'}), 200

@officeexpenditure_blueprint.route('/officeexpenditure/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_officeexpenditure(user_id, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM officeexpenditure WHERE officeexpenditureid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Office Expenditure deleted'}), 200