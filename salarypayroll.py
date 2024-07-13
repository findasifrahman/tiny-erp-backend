#salarypayroll: payrollid serial not null,  maincompanyid int not null unchangeable, employeeid INT not null, employeename varchar(128) not null, date TimeStamp nut null, 
#salary INT not null, deduction NOT NULL default 0 INT, bonus NOT NULL DEFAULT 0 
#INT, leavetaken not null default 0, finalsalarypaid INT not NULL, createdat (TIMESTAMP)


from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2

import azure.functions as func
salarypayroll_blueprint = func.Blueprint('salarypayroll', __name__)


@salarypayroll_blueprint.route('/salarypayroll', methods=['POST'])
@cross_origin()
@token_required
def add_salarypayroll():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO salarypayroll (maincompanyid, employeeid, employeename, date, salary, deduction, bonus, leavetaken, finalsalarypaid, createdat) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)''',
        (data['maincompanyid'], data['employeeid'], data['employeename'], data['date'], data['salary'], data['deduction'], data['bonus'], data['leavetaken'], data['finalsalarypaid'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Salary Payroll added'}), 201

@salarypayroll_blueprint.route('/salarypayroll/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_salarypayrolls(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = '''
        SELECT * FROM salarypayroll where maincompanyid = %s AND date >= NOW() - INTERVAL '3 MONTHS'
        ORDER BY date DESC
    '''
    cursor.execute(query, (maincompanyid))
    salarypayrolls = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(salarypayrolls), 200

@salarypayroll_blueprint.route('/salarypayroll/getall/<maincompanyid>', methods=['GET'])
@cross_origin()
@token_required
def get_salarypayrolls_getall(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM salarypayroll where maincompanyid = %s', (maincompanyid))
    salarypayrolls = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(salarypayrolls), 200

@salarypayroll_blueprint.route('/salarypayroll/getbyid', methods=['GET'])
@cross_origin()
@token_required
def get_salarypayroll_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM salarypayroll WHERE payrollid = %s', (id,))
    salarypayroll = cursor.fetchone()
    cursor.close()
    conn.close()
    if not salarypayroll:
        return jsonify({'message': 'Salary Payroll not found'}), 404
    return jsonify(salarypayroll), 200

@salarypayroll_blueprint.route('/salarypayroll/update', methods=['POST'])
@cross_origin()
@token_required
def update_salarypayroll():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE salarypayroll SET employeeid = %s, employeename = %s, date = %s, salary = %s, deduction = %s, bonus = %s, leavetaken = %s, finalsalarypaid = %s 
           WHERE payrollid = %s''',
        (data['employeeid'], data['employeename'], data['date'], data['salary'], data['deduction'], data['bonus'], data['leavetaken'], data['finalsalarypaid'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Salary Payroll updated'}), 200

@salarypayroll_blueprint.route('/salarypayroll', methods=['DELETE'])
@cross_origin()
@token_required
def delete_salarypayroll():
    id = request.args.get('id')
    maincompanyid = request.args.get('maincompanyid')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    error = False
    try:
        cursor.execute('DELETE FROM salarypayroll WHERE payrollid = %s', (id,))
        conn.commit()
        
        query = '''
            SELECT * FROM salarypayroll where maincompanyid = %s AND date >= NOW() - INTERVAL '3 MONTHS'
            ORDER BY date DESC
        '''
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
            return jsonify({'status': 'salarypayroll deleted', 'data': roles}), 200