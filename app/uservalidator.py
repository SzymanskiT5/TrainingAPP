import random
import string
import sys
from datetime import datetime, timedelta, date
from flask_recaptcha import ReCaptcha
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from app.constans import EMAIL_PATTERN, PASSWORD_PATTERN
from app.exceptions import *
from app.models import Users
from app import db, recaptcha
import re
from app.mailhandler import MailHandler
from typing import Tuple


class UserValidator:
    '''Controlling class'''

    @staticmethod
    def get_id_by_nick(nick: str) -> int:
        found_id = db.session.query(Users).filter(Users.name == nick).first()
        db.session.commit()
        return found_id._id

    @staticmethod
    def get_id_by_email(email):
        found_id = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        return found_id._id


    @staticmethod
    def check_email_format(email: str):
        if not (re.match(EMAIL_PATTERN, email)):
            raise WrongEmailFormat

    @staticmethod
    def check_password_format(password: str):
        if not (re.match(PASSWORD_PATTERN, password)):
            raise FalsePasswordFormat

    @staticmethod
    def check_nick_lenght(nick: str):
        if not len(nick) < 81:
            raise TooLongNick

    @staticmethod
    def check_if_email_exits(email: str):
        found_email = db.session.query(Users.email).filter(Users.email == email).first()
        db.session.commit()
        if found_email:
            raise EmailExists

    @staticmethod
    def check_if_email_doesnt_exists(email: str):
        found_email = db.session.query(Users.email).filter(Users.email == email).first()
        db.session.commit()
        if not found_email:
            raise EmailRegistrationDoesntExists

    @staticmethod
    def check_if_nick_exists(nick: str):
        found_nick = Users.query.filter_by(name=nick).first()
        db.session.commit()
        if found_nick:
            raise NickExists

    @staticmethod
    def get_email_from_nick(nick: str) -> str:
        found_email = db.session.query(Users).filter(Users.name == nick).first()
        db.session.commit()
        return found_email.email

    @staticmethod
    def get_nick_from_email(email: str) -> str:
        found_nick = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        return found_nick.name

    @staticmethod
    def compare_activation_code_with_code_from_base(email: str, activation_code: str) -> None:
        found_code = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        if found_code.activation_code != activation_code:
            raise WrongCodeOrEmail

    @staticmethod
    def get_password_from_email(email: str) -> str:
        found_password = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        return found_password.password_hash

    @staticmethod
    def compare_expire_date_with_current_date(email: str) -> None:
        found_expiration_date = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        found_expiration_date = found_expiration_date.expire_date
        if found_expiration_date < datetime.now():
            raise CodeExpired

    @staticmethod
    def check_hashed_password(entered_password: str, password: str, nick: str, email: str) -> Tuple:
        if check_password_hash(entered_password, password):
            return "Successfully logged in", "success", nick, email
        return "Wrong nickname/email or password", "error", None, None

    @staticmethod
    def check_if_user_activated_from_email(email: str):
        found_activated = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        if found_activated.is_activated:
            raise AccountIsActivated

    @staticmethod
    def check_if_user_activated_from_nick(nick: str) -> int:
        activation = db.session.query(Users).filter(Users.name == nick).first()
        db.session.commit()
        return activation.is_activated

    @staticmethod
    def create_user(nick: str, email: str, secured_password: str, activation_code: str, expire_date: datetime) -> None:
        new_user = Users(name=nick, email=email, password_hash=secured_password, activation_code=activation_code,
                         is_activated=0, expire_date=expire_date)
        db.session.add(new_user)
        db.session.commit()

    @staticmethod
    def set_expire_date() -> datetime:
        now = datetime.now()
        expire_date = now + timedelta(minutes=30)
        return expire_date

    @staticmethod
    def delete_user(email: str) -> None:
        Users.query.filter(Users.email == email).delete()
        db.session.commit()

    @staticmethod
    def create_activation_code() -> str:
        activation_code = ''.join(random.choice(string.printable) for i in range(8))
        return activation_code

    @staticmethod
    def delete_activation_code(email: str) -> None:
        activation_code = db.session.query(Users).filter(Users.email == email).first()
        activation_code.activation_code = None
        db.session.commit()

    @staticmethod
    def delete_expiration_date(email: str) -> None:
        expiration_date = db.session.query(Users).filter(Users.email == email).first()
        expiration_date.expire_date = None
        db.session.commit()

    @staticmethod
    def set_is_activated_true(email: str) -> None:
        is_activated = db.session.query(Users).filter(Users.email == email).first()
        is_activated.is_activated = 1
        db.session.commit()

    @staticmethod
    def check_if_activated(email):
        is_activated = db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        return is_activated

    @staticmethod
    def check_entered_password_with_base(email, entered_password):
        password = UserValidator.get_password_from_email(email)
        return bool(check_password_hash(password, entered_password))

    @staticmethod
    def check_login(nick_or_email: str, password: str) -> Tuple:
        if recaptcha.verify():
            try:
                UserValidator.check_if_email_exits(nick_or_email)
                UserValidator.check_if_nick_exists(nick_or_email)
                return "Wrong nickname/email/password", "warning", None, None


            except EmailExists:
                email = nick_or_email
                nick = UserValidator.get_nick_from_email(email)
                UserValidator.check_if_activated(email)
                if UserValidator.check_entered_password_with_base(email, password):
                    return "You are successfully logged in", "success", nick, email
                return "Wrong nickname/email/password or not activated", "warning", None, None



            except NickExists:
                nick = nick_or_email
                email = UserValidator.get_email_from_nick(nick)
                UserValidator.check_if_activated(email)
                if UserValidator.check_entered_password_with_base(email, password):
                    return "You are successfully logged in", "success", nick, email
                return "Wrong nickname/email/password or not activated", "warning", None, None

        return "You need to prove captcha", "warning", None, None

    @staticmethod
    def check_registration(email: str, activation_code: str) -> Tuple:
        try:
            UserValidator.check_recaptcha()
            UserValidator.check_if_email_doesnt_exists(email)
            UserValidator.check_if_user_activated_from_email(email)
            UserValidator.compare_expire_date_with_current_date(email)
            UserValidator.compare_activation_code_with_code_from_base(email, activation_code)
            UserValidator.delete_activation_code(email)
            UserValidator.set_is_activated_true(email)

            return "Now you can log in!", "success"

        except EmailRegistrationDoesntExists:
            return "Wrong activation code or email", "warning"

        except CodeExpired:
            UserValidator.delete_user(email)
            return "Code expired, you need to add new account, your account has been deleted", "error"

        except WrongCodeOrEmail:
            return "Wrong activation code or email", "warning"

        except AccountIsActivated:
            return "You are already activated!", "success"

        except RecaptchaIsMissing:
            return "You need to prove captcha", "warning"

    @staticmethod
    def handle_password_recovery(email):
        try:
            UserValidator.check_if_email_exits(email)
            return "There is no such email", "warning"
        except EmailExists:
            return "Check your mailbox and follow the instructions", "success"

    @staticmethod
    def compare_entered_passport_with_password_from_base(email: str, entered_password: str):
        if not UserValidator.check_entered_password_with_base(email, entered_password):
            raise EnteredPasswordIncorrect

    @staticmethod
    def compare_password_with_password_confirm(password: str, password_confirm: str):
        if password != password_confirm:
            raise PasswordsAreNotTheSame

    @staticmethod
    def change_password_in_base(email, new_password):
        password = db.session.query(Users).filter(Users.email == email).first()
        password.password_hash = generate_password_hash(new_password)
        db.session.commit()

    @staticmethod
    def handle_change_password(entered_password, new_password, new_password_confirm):
        email = session['email']
        try:
            UserValidator.compare_entered_passport_with_password_from_base(email, entered_password)
            UserValidator.compare_password_with_password_confirm(new_password, new_password_confirm)
            UserValidator.check_password_format(new_password)
            UserValidator.check_password_format(new_password_confirm)
            UserValidator.change_password_in_base(email, new_password)
            return "Password changed!, you can log in", "success"


        except EnteredPasswordIncorrect:
            return "Wrong password", "warning"

        except PasswordsAreNotTheSame:
            return "New password are not the same", "warning"

        except FalsePasswordFormat:
            return "New password format not correct, use strong password format", "warning"

    @staticmethod
    def handle_password_recovery_after_token(password, confirm_password):
        try:
            UserValidator.check_password_format(password)
            UserValidator.check_password_format(confirm_password)
            UserValidator.compare_password_with_password_confirm(password, confirm_password)
            password = generate_password_hash(password)
            return "Password is changed!", "success", password
        except FalsePasswordFormat:
            return "Wrong Password Format", "warning", None
        except PasswordsAreNotTheSame:
            return "Passwords are not the same", "warning", None

    @staticmethod
    def check_recaptcha():
        if not recaptcha.verify():
            raise RecaptchaIsMissing

    @staticmethod
    def check_signup_email(email: str, nick: str, password: str, confirm_password: str) -> Tuple:
        try:
            UserValidator.check_recaptcha()
            UserValidator.check_email_format(email)
            UserValidator.check_if_email_exits(email)
            UserValidator.check_nick_lenght(nick)
            UserValidator.check_if_nick_exists(nick)
            UserValidator.check_password_format(password)
            UserValidator.check_password_format(confirm_password)
            UserValidator.compare_password_with_password_confirm(password, confirm_password)
            secured_password = generate_password_hash(password)
            activation_code = UserValidator.create_activation_code()
            expire_date = UserValidator.set_expire_date()
            UserValidator.create_user(nick, email, secured_password, activation_code, expire_date)
            mail = MailHandler()
            mail.create_activation_email(email, activation_code)
            return "Now you can activate your account", "success"


        except WrongEmailFormat:
            return "False email format", 'warning'

        except EmailExists:
            return "Email is already used", 'warning'

        except TooLongNick:
            return "Nick is too long! Max 80 characters", 'warning'

        except NickExists:
            return "Nick is already used", 'warning'

        except FalsePasswordFormat:
            return "False password format", "warning"

        except PasswordsAreNotTheSame:
            return "Passwords are not the same", "warning"

        except RecaptchaIsMissing:
            return "You need to prove captcha", "warning"

    @staticmethod
    def handle_account_delete(password: str, password_confirm: str) -> Tuple:
        email = session['email']
        try:
            UserValidator.compare_entered_passport_with_password_from_base(email, password)
            UserValidator.compare_password_with_password_confirm(password, password_confirm)
            UserValidator.delete_user(email)
            return "Your account deleted successfully", "success"

        except EnteredPasswordIncorrect:
            return "Wrong password", "warning"

        except PasswordsAreNotTheSame:
            return "Passwords are not the same", "warning"
