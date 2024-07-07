# create empyee database blueprint api below exact pattern like customer.py with following database parameter.  
""" 
    employee: employyeid serial primary key, maincompanyid int not null, joiningdate timestamp not null,employeename varchar(128) not null, age int noy null, 
    contactno varchar(30) not null, address varchar(256) not null, 
    nidnumber varchar (20), salary int not null, grade varchar(10), roleid int not null, state varchar(20),description text, image bytea, createdat timestamp
 """    

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required
import psycopg2
employee_blueprint = Blueprint('employee', __name__)

@employee_blueprint.route('/employee', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def add_employee():
    # Implement the logic to add an employee
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO employee (maincompanyid, joiningdate, employeename, age, contactno, address, nidnumber, salary, grade, roleid, state, description, image, createdat) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)',
            (data['maincompanyid'], data['joiningdate'], data['employeename'], data['age'], data['contactno'], data['address'], data['nidnumber'], data['salary'], data['grade'], data['roleid'], data['state'], data['description'], data['image'])
        )
        conn.commit()
        return jsonify({'status': 'Employee added successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
    pass

@employee_blueprint.route('/employee/<maincompanyid>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_employees(maincompanyid):
    # Implement the logic to get employees by maincompanyid
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM employee where maincompanyid = %s', (maincompanyid))
    users = cursor.fetchall()
    print("users--",users)
    cursor.close()
    conn.close()
    return jsonify(users), 200

@employee_blueprint.route('/employee/getbyid', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_employee_by_id():
    # Implement the logic to get an employee by id
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM employee WHERE employeeid = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user), 200

@employee_blueprint.route('/employee/update', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def update_employee():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE employee SET maincompanyid = %s, joiningdate = %s, employeename = %s, age = %s, contactno = %s, address = %s, nidnumber = %s, salary = %s, grade = %s, roleid = %s, state = %s, description = %s, image = %s WHERE employeeid = %s',
        (data['maincompanyid'], data['joiningdate'], data['employeename'], data['age'], data['contactno'], data['address'], data['nidnumber'], data['salary'], data['grade'], data['roleid'], data['state'], data['description'], data['image'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Employee updated'}), 200

@employee_blueprint.route('/employee/<int:id>', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
@token_required
def delete_employee(id):
    # Implement the logic to delete an employee by id
    conn = get_db_connection()
    cursor = conn.cursor()
    error = False
    try:
        cursor.execute('DELETE FROM employee WHERE employeeid = %s', (id,))
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
            return jsonify({'status': 'Employee deleted'}), 200