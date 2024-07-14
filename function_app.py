import azure.functions as func
import logging
from app import app as flask_app
from azure.functions import WsgiMiddleware

#app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


from flask import Flask, request, jsonify
from flask_cors import CORS

from auth import generate_token, token_required
from psycopg2.extras import RealDictCursor
from dbcon import get_db_connection
import azure.functions as func

# from users import user_blueprint
# from maincompany import maincompany_blueprint
# from roles import roles_blueprint
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

from flask_cors import cross_origin

#app = Flask(__name__)
#app = func.FunctionApp()
#flask_app = Flask(__name__) 
app = Flask(__name__)

flask_app = func.FunctionApp()
#CORS(app)  # Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

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


# Dummy user data for authentication
users = {
    "user1": "password1",
    "user2": "password2"
}

@flask_app.route('login', methods=['POST'])
@cross_origin(origins="http://localhost:4200")
def login(req: func.HttpRequest,):
    with app.app_context():
        data = request.json
        username = data.get('username')
        password = data.get('password')

        print("login data-",data)

        query = f'''
        SELECT u.*, m.companyname
        FROM users u
        JOIN maincompany m ON u.maincompanyid = m.maincompanyid
        WHERE u.username = %s AND u.password = %s
        '''
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query,(username, password))#('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        print("login user--",user)
        cursor.close()
        conn.close()

        # if user:
        #     token = generate_token(user['username'], user['roleid'])
        #     print("generated token--",token)
        #     print(user)
        #     return jsonify({'token': token, "maincompanyid": user['maincompanyid'], "maincompanyname": user['companyname'] }), 200
        # return jsonify({'message': 'Invalid credentials'}), 401
        if user:
            token = generate_token(user['username'], user['roleid'])
            logging.info(f'Generated token: {token}')
            return func.HttpResponse(
                jsonify({'token': token, "maincompanyid": user['maincompanyid'], "maincompanyname": user['companyname']}).get_data(as_text=True),
                mimetype="application/json",
                status_code=200
            )
        return func.HttpResponse(
            jsonify({'message': 'Invalid credentials'}).get_data(as_text=True),
            mimetype="application/json",
            status_code=401
        )

@flask_app.route('change-password', methods=['POST'])
#@cross_origin()  # Enable CORS for this route
def changePassword(req: func.HttpRequest):
    data = request.json
    print(data)
    username = data.get('username')
    password = data.get('newPassword')
    oldPassword = data.get('oldPassword')
    print(data)

    print(username)
    print(password)

    query = f'''
    SELECT username, password
    FROM users 
    WHERE username = %s AND password = %s
    '''
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query,(username, oldPassword))
    user = cursor.fetchone()
    print("login user--",user)
    if user:
        cursor.execute('UPDATE users SET password = %s WHERE username = %s', (password, username))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Password changed successfully'}), 200
    cursor.close()
    conn.close()
    return jsonify({'message': 'Invalid credentials'}), 401

#######test#
@flask_app.route('user/{maincompanyid}', methods=['GET'])
#@cross_origin()  # Enable CORS for this route
async def get_al_users(req: func.HttpRequest):
    with app.app_context():
        maincompanyid = req.route_params.get('maincompanyid')
        print("maincompanyid--",maincompanyid)
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM users where maincompanyid = %s', (maincompanyid,))
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        response_data = jsonify(users).get_data(as_text=True)
        return func.HttpResponse(response_data, mimetype="application/json", status_code=200)
        #return jsonify(users), 200


#############

# Create an Azure Function which serves the above routes in our WSGI runtime (Gunicorn)
#app = func.WsgiFunctionApp(app=flask_app.wsgi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
# Azure Functions entry point
# def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')
#     return WsgiMiddleware(app).handle(req, context)

#def main(req: func.HttpRequest) -> func.HttpResponse:
#    return func.WsgiMiddleware(app.wsgi_app).handle(req)





