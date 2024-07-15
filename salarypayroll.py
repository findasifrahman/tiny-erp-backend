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
from mapp import create_app
app = create_app()#Flask(__name__)
salarypayroll_blueprint = func.Blueprint('salarypayroll', __name__)


@salarypayroll_blueprint.route('salarypayroll', methods=['POST'])
#@cross_origin()
#@token_required
def add_salarypayroll(req: func.HttpRequest):
    data = req.get_json()
    with app.app_context():
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
        return func.HttpResponse(jsonify({'status': 'Salary Payroll'}).get_data(as_text=True), mimetype="application/json", status_code=201)


@salarypayroll_blueprint.route('salarypayroll/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_salarypayrolls(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
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
        response_data = jsonify(salarypayrolls).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@salarypayroll_blueprint.route('salarypayroll-getall/{maincompanyid}', methods=['GET'])
#@cross_origin()
#@token_required
def get_salarypayrolls_getall(req: func.HttpRequest):
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM salarypayroll where maincompanyid = %s', (maincompanyid))
        salarypayrolls = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(salarypayrolls).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@salarypayroll_blueprint.route('salarypayroll-getbyid', methods=['GET'])
#@cross_origin()
#@token_required
def get_salarypayroll_by_id(req: func.HttpRequest):
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM salarypayroll WHERE payrollid = %s', (id,))
        salarypayroll = cursor.fetchone()
        cursor.close()
        conn.close()
        if not salarypayroll:
            return func.HttpResponse(jsonify({'status': 'Salary payrollnot found'}).get_data(as_text=True), mimetype="application/json", status_code=404)

        response_data = jsonify(salarypayroll).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)

@salarypayroll_blueprint.route('salarypayroll-update', methods=['POST'])
#@cross_origin()
#@token_required
def update_salarypayroll(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
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
        return func.HttpResponse(jsonify({'status': 'Salary Payroll updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@salarypayroll_blueprint.route('salarypayroll', methods=['DELETE'])
#@cross_origin()
#@token_required
def delete_salarypayroll(req: func.HttpRequest):
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
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
            return func.HttpResponse(jsonify({'message': str(e)}).get_data(as_text=True), mimetype="application/json", status_code=400)
        finally:
            cursor.close()
            conn.close()
            if not error:
                return func.HttpResponse(jsonify({'status': 'payroll deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)
