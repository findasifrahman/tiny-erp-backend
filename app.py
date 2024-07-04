# app.py
from flask import Flask
from flask_cors import CORS
from users import user_blueprint
from maincompany import maincompany_blueprint
from roles import roles_blueprint
from customer import customer_blueprint

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register blueprints
app.register_blueprint(user_blueprint)
app.register_blueprint(maincompany_blueprint)
app.register_blueprint(roles_blueprint)
app.register_blueprint(customer_blueprint )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
