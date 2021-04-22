import random
import string
from datetime import datetime, timedelta, date
from flask import flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app.constans import EMAIL_PATTERN, PASSWORD_PATTERN
from app.exceptions import CodeExpired, WrongCodeOrEmail
from app.models import Users
from app import db
import re
import sys
from app.mailhandler import MailHandler

class UserValidator:
    '''Controlling class'''
    def __init__(self):
        self.mail = MailHandler()

    @staticmethod
    def get_id_by_nick(nick):
        found_id = db.session.query(Users).filter(Users.name == nick).first()
        db.session.commit()

        return found_id._id

    @staticmethod
    def check_email_format(email):
        return bool(re.match(EMAIL_PATTERN, email))

    @staticmethod
    def check_password_format(password):
        return bool(re.match(PASSWORD_PATTERN, password))

    @staticmethod
    def check_nick_lenght(nick):
        return len(nick) < 81

    @staticmethod
    def check_if_email_exits(email):
        found_email = Users.query.filter_by(email=email).first()
        db.session.commit()
        return bool(found_email)

    @staticmethod
    def check_if_nick_exists(nick):
        found_nick = Users.query.filter_by(name=nick).first()
        db.session.commit()
        return bool(found_nick)

    @staticmethod
    def get_email_from_nick(nick):
        found_email = db.session.query(Users).filter(Users.name == nick).first()
        db.session.commit()
        return found_email.email

    @staticmethod
    def get_nick_from_email(email):
        found_nick = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        return found_nick.name

    @staticmethod
    def compare_activation_code_with_code_from_base(email, activation_code):
        found_code = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        if found_code.activation_code != activation_code:
            raise WrongCodeOrEmail

    @staticmethod
    def get_password_from_email(email):
        found_password = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        return found_password.password_hash

    @staticmethod
    def compare_expire_date_with_current_date(email):
        found_expiration_date = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        found_expiration_date = found_expiration_date.expire_date
        if  found_expiration_date < datetime.now():
            raise CodeExpired



    @staticmethod
    def check_hashed_password(entered_password, password, nick, email):
        if check_password_hash(entered_password, password):
            return "Successfully logged in", "success", nick, email
        return "Wrong nickname/email or password", "error", None, None


    @staticmethod
    def check_if_user_activated_from_email(email):
        activation = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        return activation.is_activated

    @staticmethod
    def check_if_user_activated_from_nick(nick):
        activation = db.session.query(Users).filter(Users.name == nick).first()
        db.session.commit()
        return activation.is_activated

    @staticmethod
    def check_login(nick_or_email, password):
        email = UserValidator.check_if_email_exits(nick_or_email)
        nick = UserValidator.check_if_nick_exists(nick_or_email)
        # is_activated_nick = UserValidator.check_if_user_activated_from_nick(nick)
        # is_activated_email = UserValidator.check_if_user_activated_from_email(email)

        if email:
            email = nick_or_email
            nick = UserValidator.get_nick_from_email(email)
            entered_password = UserValidator.get_password_from_email(email)
            is_activated_email = UserValidator.check_if_user_activated_from_email(email)
            if is_activated_email:
                return UserValidator.check_hashed_password(entered_password, password, nick, email)


        elif nick:
            nick = nick_or_email
            email = UserValidator.get_email_from_nick(nick_or_email)
            entered_password = UserValidator.get_password_from_email(email)
            is_activated_email = UserValidator.check_if_user_activated_from_email(email)
            if is_activated_email:
                return UserValidator.check_hashed_password(entered_password, password, nick, email)



        return "Wrong nickname/email/password or not activated", "error", None, None


    @staticmethod
    def create_user(nick:str, email:str, secured_password: str, activation_code:str, expire_date:datetime) -> None:
        new_user = Users(name=nick, email=email, password_hash=secured_password, activation_code=activation_code,
                         is_activated=0, expire_date=expire_date)
        db.session.add(new_user)
        db.session.commit()

    @staticmethod
    def set_expire_date():
        now = datetime.now()
        expire_date = now + timedelta(minutes=5)
        return expire_date

    @staticmethod
    def delete_user(email):
        Users.query.filter_by(email=email).delete()
        db.session.commit()

    @staticmethod
    def create_activation_code():
        activation_code = ''.join(random.choice(string.printable) for i in range(8))
        return activation_code

    @staticmethod
    def delete_activation_code(email):
        activation_code = db.session.query(Users).filter(Users.email == email).first()
        activation_code.activation_code = None
        db.session.commit()
    @staticmethod
    def delete_expiration_date(email):
        expiration_date = db.session.query(Users).filter(Users.email == email).first()
        expiration_date.expire_date = None
        db.session.commit()
    @staticmethod
    def set_is_activated_true(email):
        is_activated = db.session.query(Users).filter(Users.email == email).first()
        is_activated.is_activated = 1
        db.session.commit()

    @staticmethod
    def check_registration(email: str , activation_code: str):
        try:
            UserValidator.compare_expire_date_with_current_date(email)
            UserValidator.compare_activation_code_with_code_from_base(email, activation_code)
            UserValidator.delete_activation_code(email)
            UserValidator.set_is_activated_true(email)
            return "Now you can log in!", "success"
        except CodeExpired:
            UserValidator.delete_user(email)
            return "Code expired, you need to add new account", "error"
        except WrongCodeOrEmail:
            return "Wrong activation code or email", "warning"





    @staticmethod
    def check_signup_email( email, nick, password):
        email_format = UserValidator.check_email_format(email)

        if not email_format:
            return "False email format", 'warning'

        email_exists = UserValidator.check_if_email_exits(email)
        if email_exists:
            return "Email is already used", 'warning'

        nick_length = UserValidator.check_nick_lenght(nick)
        if not nick_length:
            return "Nick is too long! Max 80 characters", 'warning'

        nick_exists = UserValidator.check_if_nick_exists(nick)
        if nick_exists:
            return "Nick is already used", 'warning'

        password_format = UserValidator.check_password_format(password)
        if password_format:
            secured_password = generate_password_hash(password)
            activation_code = UserValidator.create_activation_code()
            expire_date = UserValidator.set_expire_date()
            UserValidator.create_user(nick, email, secured_password, activation_code, expire_date)
            mail = MailHandler()
            mail.create_email(email, activation_code)



            return "Check your mailbox to finish registration", 'success'   ##ADD CONFIRM
        return "False password format", "warning"
