# app.py
from flask import Flask

from users import user_blueprint
from maincompany import maincompany_blueprint
from roles import roles_blueprint

app = Flask(__name__)


# Register blueprints
app.register_blueprint(user_blueprint)
app.register_blueprint(maincompany_blueprint)
app.register_blueprint(roles_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
