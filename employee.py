# create empyee database blueprint api below exact pattern like customer.py with following database parameter.  
""" 
    employee: employyeid serial primary key, maincompanyid int not null, joiningdate timestamp not null,employeename varchar(128) not null, age int noy null, 
    contactno varchar(30) not null, address varchar(256) not null, 
    nidnumber varchar (20), salary int not null, grade varchar(10), roleid int not null, state varchar(20),description text, image bytea, createdat timestamp
 """    

from flask import request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2

import azure.functions as func
from mapp import create_app
app = create_app()#Flask(__name__)
employee_blueprint = func.Blueprint('employee', __name__)

@employee_blueprint.route('employee', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def add_employee(req: func.HttpRequest):
    # Implement the logic to add an employee
    data = req.get_json()
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO employee (maincompanyid, joiningdate, employeename, age, contactno, address, nidnumber, salary, grade, roleid, state, description, image, createdat) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)',
                (data['maincompanyid'], data['joiningdate'], data['employeename'], data['age'], data['contactno'], data['address'], data['nidnumber'], data['salary'], data['grade'], data['roleid'], data['state'], data['description'], data['image'])
            )
            conn.commit()
            return func.HttpResponse(jsonify({'status': 'Employee added'}).get_data(as_text=True), mimetype="application/json", status_code=201)
        
        except Exception as e:
            conn.rollback()
            return func.HttpResponse(jsonify({'message': str(e)}).get_data(as_text=True), mimetype="application/json", status_code=500)

        finally:
            cursor.close()
            conn.close()
    

@employee_blueprint.route('employee/{maincompanyid}', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_employees(req: func.HttpRequest):
    # Implement the logic to get employees by maincompanyid
    maincompanyid = req.route_params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM employee where maincompanyid = %s', (maincompanyid))
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        response_data = jsonify(users).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@employee_blueprint.route('employee-getbyid', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def get_employee_by_id(req: func.HttpRequest):
    # Implement the logic to get an employee by id
    id = req.params.get('id')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM employee WHERE employeeid = %s', (id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        response_data = jsonify(user).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)


@employee_blueprint.route('employee-update', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def update_employee(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE employee SET maincompanyid = %s, joiningdate = %s, employeename = %s, age = %s, contactno = %s, address = %s, nidnumber = %s, salary = %s, grade = %s, roleid = %s, state = %s, description = %s, image = %s WHERE employeeid = %s',
            (data['maincompanyid'], data['joiningdate'], data['employeename'], data['age'], data['contactno'], data['address'], data['nidnumber'], data['salary'], data['grade'], data['roleid'], data['state'], data['description'], data['image'], data['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return func.HttpResponse(jsonify({'status': 'Employee updated'}).get_data(as_text=True), mimetype="application/json", status_code=200)

@employee_blueprint.route('employee', methods=['DELETE'])
#@cross_origin()  # Enable CORS for this route
#@token_required
def delete_employee(req: func.HttpRequest):        
    id = req.params.get('id')#request.args.get('id')
    maincompanyid = req.params.get('maincompanyid')
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        error = False
        try:
            cursor.execute('DELETE FROM employee WHERE employeeid = %s', (id,))
            conn.commit()
            
            # Fetch the updated list of sales order details
            cursor.execute('SELECT * FROM employee where maincompanyid = %s', (maincompanyid))
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
                return func.HttpResponse(jsonify({'status': 'Employee deleted', 'data': roles}).get_data(as_text=True), mimetype="application/json", status_code=200)
