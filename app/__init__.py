from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from hashlib import md5
from flask_login import LoginManager
from flask_recaptcha import ReCaptcha

'''Initialize app configurations and endpoints'''
db = SQLAlchemy()

app = Flask(__name__)
# app.config['RECAPTCHA_SITE_KEY'] = # <-- Add your site key
# app.config['RECAPTCHA_SECRET_KEY'] =  # <-- Add your secret key
recaptcha = ReCaptcha(app)

encryptor = md5()
app.permanent_session_lifetime = timedelta(minutes=30)
app.secret_key = encryptor.digest()
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User_and_Workouts.db'
app.config['SESSION_TYPE'] = 'sqlalchemy'
db.init_app(app)
app.debug = True
from .main_app import main_blueprint, login_blueprint, my_schedule_blueprint, sign_up_blueprint, \
    activation_blueprint, my_account_blueprint, password_recovery_blueprint, reset_token_blueprint

app.register_blueprint(main_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(my_schedule_blueprint)
app.register_blueprint(sign_up_blueprint)
app.register_blueprint(activation_blueprint)
app.register_blueprint(my_account_blueprint)
app.register_blueprint(password_recovery_blueprint)
app.register_blueprint(reset_token_blueprint)
