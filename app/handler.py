from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash

from .constans import EMAIL_PATTERN, PASSWORD_PATTERN
from .models import Users
from . import db
import re


class Handler:
    '''Controlling class'''
    def __init__(self):
        self.user = Users()

    @staticmethod
    def check_email_format(email):
        return bool(re.match(EMAIL_PATTERN, email))

    @staticmethod
    def check_password_format(password):
        return bool(re.match(PASSWORD_PATTERN, password))

    @staticmethod
    def check_nick_lenght(nick):
        if len(nick) < 81:
            return True
        return False

    @staticmethod
    def check_if_email_exits(email):
        found_email = Users.query.filter_by(email=email).first()
        print(found_email)
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
    def get_password_from_email(email):
        found_password = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        return found_password.password_hash

    def check_login(self, nick_or_email, password):
        email = self.check_if_email_exits(nick_or_email)
        nick = self.check_if_nick_exists(nick_or_email)

        if email:
            email = nick_or_email
            nick = self.get_nick_from_email(email)
            get_password = self.get_password_from_email(email)
            if check_password_hash(get_password, password):
                return "Successfully logged in", "success", nick, email

        elif nick:
            nick = nick_or_email
            email = self.get_email_from_nick(nick_or_email)
            get_password = self.get_password_from_email(email)

            if check_password_hash(get_password, password):
                return "Successfully logged in", "success", nick, email

        return "Wrong nickname/email or password", "error", None, None

    def check_signup_email(self, email, nick, password):
        email_format = self.check_email_format(email)
        if not email_format:
            return ("False email format", 'warning')

        email_exists = self.check_if_email_exits(email)
        if email_exists:
            return "Email is already used", 'warning'

        nick_length = self.check_nick_lenght(nick)
        if not nick_length:
            return ("Nick is too long! Max 80 characters", 'warning')

        nick_exists = self.check_if_nick_exists(nick)
        if nick_exists:
            return "Nick is already used", 'warning'

        password_format = self.check_password_format(password)
        if password_format:
            secured_password = generate_password_hash(password)
            new_user = Users(name=nick, email=email, password_hash=secured_password)
            db.session.add(new_user)
            db.session.commit()
            return "Now you can log in!", 'success'
        return "False password format", "warning"