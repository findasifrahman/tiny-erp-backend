# salesorder:salesorderid serial p_key,maincompanyid int not null,customerid int not null, customercompany varchar(256) not null, 
# salestype varchar(20) not null, salesagent notnull varchar(128), totalamount float,
#status default pending not null varchar(50),orderdate timestamp_without_timezone, createdat timestamp without time zone

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from auth import token_required

customer_blueprint = Blueprint('customer', __name__)


@customer_blueprint.route('/salesorders', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def add_salesorders():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO salesorder (maincompanyid, customerid, customercompany, salestype, salesagent, totalamount, status, orderdate, createdat) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)',
        (data['maincompanyid'], data['customerid'], data['customercompany'], data['salestype'],data['salesagent'], data['totalamount'],data['status'],data['orderdate'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'Salesorder added'}), 201

@customer_blueprint.route('/salesorders/<maincompanyid>', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_salesorders(maincompanyid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM salesorder where maincompanyid = %s', (maincompanyid))
    users = cursor.fetchall()
    print("users--",users)
    cursor.close()
    conn.close()
    return jsonify(users), 200

@customer_blueprint.route('/salesorders/getbyid', methods=['GET'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_salesorders_by_id():
    id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM salesorder WHERE salesorderid = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(user), 200

@customer_blueprint.route('/salesorders/update', methods=['POST'])
@cross_origin()  # Enable CORS for this route
@token_required
def update_salesorders_customer():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE salesorder SET maincompanyid = %s, customerid = %s, customercompany = %s, salestype = %s, salesagent = %s, totalamount = %s, status = %s, orderdate= %s WHERE salesorderid = %s',
        (data['maincompanyid'], data['customerid'], data['customercompany'], data['salestype'],data['salesagent'], data['totalamount'],data['status'],data['orderdate'], data['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User updated'}), 200

@customer_blueprint.route('/salesorders/<int:id>', methods=['DELETE'])
@cross_origin()  # Enable CORS for this route
@token_required
def delete_salesorders_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM salesorder WHERE salesorderid = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'User deleted'}), 200
