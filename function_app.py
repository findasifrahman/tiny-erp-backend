import logging
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import azure.functions as func
from auth import generate_token, token_required
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from dbcon import get_db_connection
from mapp import create_app


from users import user_blueprint
from roles import roles_blueprint
from supplier import supplier_blueprint
from salesorders import salesorders_blueprint
# from maincompany import maincompany_blueprint
# from customer import customer_blueprint
# from employee import employee_blueprint
# from salesorders import salesorders_blueprint
# from productcategory import productcategory_blueprint
# from productsubcategory import productsubcategory_blueprint
# from salesorderdetails import salesorderdetails_blueprint
# from paymentsales import paymentsales_blueprint
# from purchasecategory import purchasecategory_blueprint
# from purchasesubcategory import purchasesubcategory_blueprint
# from supplier import supplier_blueprint
# from purchaseorder import purchaseorder_blueprint
# from purchaseorderdetail import purchaseorderdetail_blueprint
# from salarypayroll import salarypayroll_blueprint
# from officepurchaseitemlist import officepurchaseitemlist_blueprint
# from officeexpenditure import officeexpenditure_blueprint
# from assets import assets_blueprint
# from productstock import productstock_blueprint

# Register blueprints
# app.register_blueprint(user_blueprint)
# app.register_blueprint(maincompany_blueprint)
# app.register_blueprint(roles_blueprint)
# app.register_blueprint(customer_blueprint )

# app.register_blueprint(employee_blueprint)
# app.register_blueprint(salesorders_blueprint)
# app.register_blueprint(salesorderdetails_blueprint)
# app.register_blueprint(productcategory_blueprint)
# app.register_blueprint(productsubcategory_blueprint)
# app.register_blueprint(paymentsales_blueprint)
# app.register_blueprint(purchasecategory_blueprint)
# app.register_blueprint(purchasesubcategory_blueprint)
# app.register_blueprint(supplier_blueprint)
# app.register_blueprint(purchaseorder_blueprint)
# app.register_blueprint(purchaseorderdetail_blueprint)
# app.register_blueprint(salarypayroll_blueprint)
# app.register_blueprint(officepurchaseitemlist_blueprint)
# app.register_blueprint(officeexpenditure_blueprint)
# app.register_blueprint(assets_blueprint)
# app.register_blueprint(productstock_blueprint)



app = create_app()#Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

function_app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


##
function_app.register_functions(user_blueprint)
function_app.register_functions(roles_blueprint)
function_app.register_functions(supplier_blueprint)
function_app.register_functions(salesorders_blueprint)
##

@function_app.route(route="login", methods=["POST", "OPTIONS"])
async def login(req: func.HttpRequest):
    if req.method == "OPTIONS":
        return func.HttpResponse(
            headers={
                "Access-Control-Allow-Origin": "http://localhost:4200",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            status_code=204
        )

    with app.app_context():
        data = req.get_json()
        username = data.get('username')
        password = data.get('password')

        logging.info(f'Login data: {data}')

        query = '''
        SELECT u.*, m.companyname
        FROM users u
        JOIN maincompany m ON u.maincompanyid = m.maincompanyid
        WHERE u.username = %s AND u.password = %s
        '''
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            token = generate_token(user['username'], user['roleid'])
            logging.info(f'Generated token: {token}')
            return func.HttpResponse(
                jsonify({'token': token, "maincompanyid": user['maincompanyid'], "maincompanyname": user['companyname']}).get_data(as_text=True),
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "http://localhost:4200"},
                status_code=200
            )
        return func.HttpResponse(
            jsonify({'message': 'Invalid credentials'}).get_data(as_text=True),
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "http://localhost:4200"},
            status_code=401
        )

@function_app.route(route="change-password", methods=["POST"])
@cross_origin(origins="http://localhost:4200")
async def change_password(req: func.HttpRequest):
    with app.app_context():
        data = req.get_json()
        username = data.get('username')
        password = data.get('newPassword')
        old_password = data.get('oldPassword')

        query = '''
        SELECT username, password
        FROM users 
        WHERE username = %s AND password = %s
        '''
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (username, old_password))
        user = cursor.fetchone()
        
        if user:
            cursor.execute('UPDATE users SET password = %s WHERE username = %s', (password, username))
            conn.commit()
            cursor.close()
            conn.close()
            return func.HttpResponse(
                jsonify({'message': 'Password changed successfully'}).get_data(as_text=True),
                mimetype="application/json",
                status_code=200
            )

        cursor.close()
        conn.close()
        return func.HttpResponse(
            jsonify({'message': 'Invalid credentials'}).get_data(as_text=True),
            mimetype="application/json",
            status_code=401
        )


