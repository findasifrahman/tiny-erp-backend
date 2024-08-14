import logging
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import azure.functions as func
from auth import generate_token, token_required, decode_token
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
from dbcon import get_db_connection
from mapp import create_app


from users import user_blueprint
from roles import roles_blueprint


from maincompany import maincompany_blueprint
from customer import customer_blueprint
from employee import employee_blueprint
from salesorders import salesorders_blueprint
from productcategory import productcategory_blueprint
from productsubcategory import productsubcategory_blueprint
from salesorderdetails import salesorderdetails_blueprint
from paymentsales import paymentsales_blueprint
from purchasecategory import purchasecategory_blueprint
from purchasesubcategory import purchasesubcategory_blueprint
from supplier import supplier_blueprint
from purchaseorder import purchaseorder_blueprint
from purchaseorderdetail import purchaseorderdetail_blueprint
from salarypayroll import salarypayroll_blueprint
from officepurchaseitemlist import officepurchaseitemlist_blueprint
from officeexpenditure import officeexpenditure_blueprint
from assets import assets_blueprint
from productstock import productstock_blueprint
from purchasepayment import purchasepayment_blueprint




app = create_app()#Flask(__name__)

CORS(app)#, resources={r"/*": {"origins": "https://proud-ocean-0ed2e3100.5.azurestaticapps.net"}})

function_app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


##
function_app.register_functions(user_blueprint)
#app.register_blueprint(user_blueprint)

function_app.register_functions(roles_blueprint)
function_app.register_functions(supplier_blueprint)
function_app.register_functions(salesorders_blueprint)
function_app.register_functions(salesorderdetails_blueprint)
function_app.register_functions(purchasecategory_blueprint)
function_app.register_functions(purchasesubcategory_blueprint)
function_app.register_functions(purchaseorder_blueprint)
function_app.register_functions(purchaseorderdetail_blueprint)
function_app.register_functions(productcategory_blueprint)
function_app.register_functions(productsubcategory_blueprint)
function_app.register_functions(customer_blueprint)
function_app.register_functions(employee_blueprint)
function_app.register_functions(maincompany_blueprint)
function_app.register_functions(salarypayroll_blueprint)
function_app.register_functions(paymentsales_blueprint)
function_app.register_functions(officepurchaseitemlist_blueprint)
function_app.register_functions(officeexpenditure_blueprint)
function_app.register_functions(assets_blueprint)
function_app.register_functions(productstock_blueprint)
function_app.register_functions(purchasepayment_blueprint)
##
'''
def dispatch_request(req: func.HttpRequest, route_prefix: str):
    with app.app_context():
        token = req.headers.get('Authorization')
        if token:
            # If token is present, validate it
            is_valid = decode_token(token)  # Implement validate_token according to your logic
            if not is_valid['user']:
                return func.HttpResponse(
                    "Unauthorized",
                    status_code=401,
                    headers={"Access-Control-Allow-Origin": "*"}
                )

        # Create the URL with query parameters
        path = f"/{route_prefix}/{req.route_params.get('*route')}"
        query_string = req.url.split('?')[1] if '?' in req.url else ''
        full_path = f"{path}?{query_string}" if query_string else path

        with app.test_request_context(full_path, method=req.method, data=req.get_body(), headers=dict(req.headers)):
            response = app.full_dispatch_request()
            return func.HttpResponse(
                response.get_data(as_text=True),
                status_code=response.status_code,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS, GET, DELETE",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                },
                mimetype="application/json"
            )



@function_app.route(route="users/{*route}", methods=["GET", "POST", "OPTIONS", "DELETE"])
async def users_dispatcher(req: func.HttpRequest):
    logging.info(f'users_dispatcher is --------------------------- {req.route_params.get("maincompanyid")} ')
    logging.info(f'users_dispatcher rote is --------------------------- {req.route_params} ')

    return dispatch_request(req, "users")
'''
##
@function_app.route(route="login", methods=["POST", "OPTIONS"])
async def login(req: func.HttpRequest):
    if req.method == "OPTIONS":
        return func.HttpResponse(
            headers={
                "Access-Control-Allow-Origin": "https://proud-ocean-0ed2e3100.5.azurestaticapps.net",
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


