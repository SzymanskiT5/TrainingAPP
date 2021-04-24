from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from hashlib import md5

'''Initialize app configurations and endpoints'''
db = SQLAlchemy()


def create_app() -> Flask:
    app = Flask(__name__, static_folder='/static')
    encryptor = md5()
    app.permanent_session_lifetime = timedelta(minutes=30)
    app.secret_key = encryptor.digest()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User_and_Workouts.db'
    db.init_app(app)
    app.debug = True
    from .main_app import main_blueprint, login_blueprint, my_schedule_blueprint, sign_up_blueprint, registration_blueprint, my_account_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(login_blueprint)
    app.register_blueprint(my_schedule_blueprint)
    app.register_blueprint(sign_up_blueprint)
    app.register_blueprint(registration_blueprint)
    app.register_blueprint(my_account_blueprint)
    return app

