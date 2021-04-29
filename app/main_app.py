import sys

from flask import render_template, redirect, url_for, Blueprint, request, session, flash, Response, current_app
from . import db, recaptcha
from .mailhandler import MailHandler
from .uservalidator import UserValidator
from typing import Union
from .models import Training, Users
from datetime import date

main_blueprint = Blueprint('main', __name__)
login_blueprint = Blueprint('login', __name__)
my_schedule_blueprint = Blueprint('myschedule', __name__)
sign_up_blueprint = Blueprint("signup", __name__)
logout_blueprint = Blueprint("logout", __name__)
activation_blueprint = Blueprint("activation", __name__)
my_account_blueprint = Blueprint("myaccount", __name__)
change_password_blueprint = Blueprint("change_password", __name__)
delete_account_blueprint = Blueprint("delete_account", __name__)
password_recovery_blueprint = Blueprint("password_recovery", __name__)
reset_token_blueprint = Blueprint("reset_token", __name__)
events = [
    {
        "name": " test",
        "date": "2021-04-20",
        "duration": "60",
        "note": "FAJNIE",
        "rate": 5,

    }

]


def add_training(name, training_date, duration, note, rate, user_id) -> None:
    training = Training(name=name, date=training_date, duration=duration, note=note, rate=rate, user_id=int(user_id))
    db.session.add(training)
    db.session.commit()


def create_date_object(training_date):
    """SQL needs python data format"""
    date_time_object = date.fromisoformat(training_date)
    return date_time_object


def check_if_logged_in(template_name: str) -> Union[Response, str]:
    if "nick" in session:
        flash('You are already logged in', 'success')
        return redirect(url_for("main.main"))

    return render_template(template_name)


def check_if_logged_in_account_options(template: str):
    if "nick" in session:
        return render_template(template)
    flash("You need to log in to check account options", 'warning')
    return redirect(url_for("login.login"))


def check_if_logged_myschedule() -> Union[Response, str]:
    if "nick" in session:
        return render_template("eventcalendar_create-read-update-delete-CRUD.html")
    flash("You need to log in to check the schedule", 'warning')
    return redirect(url_for("login.login"))


def handle_login(email_or_nick: str, password: str) -> Union[Response, str]:
    flashpop, message, nickname, email = UserValidator.check_login(email_or_nick, password)

    flash(flashpop, message)
    if message == 'success':
        session.update({"nick": nickname, "email": email})
        return redirect(url_for("main.main"))
    return render_template("login.html")


@main_blueprint.route('/', methods=["GET"])
def main():
    return render_template('main.html')


@login_blueprint.route('/login', methods=["POST", "GET"])
def login() -> Union[Response, str]:
    if request.method == "POST":
        session.permanent = True
        email_or_nick = request.form['nickname']
        password = request.form['password']

        return handle_login(email_or_nick, password)

    elif request.method == "GET":
        return check_if_logged_in("login.html")


@my_schedule_blueprint.route('/myschedule', methods=["POST", "GET"])
def my_schedule() -> Union[Response, str]:
    if request.method == "POST":
        name = request.form['name']
        training_date = request.form['date']
        training_date = create_date_object(training_date)
        duration = request.form['duration']
        note = request.form['note']
        rate = request.form['rate']
        nick = session["nick"]
        user_id = UserValidator.get_id_by_nick(nick)
        add_training(name, training_date, duration, note, rate, user_id)
        flash("Training added!", "success")
        return render_template("eventcalendar_create-read-update-delete-CRUD.html")

    elif request.method == "GET":
        return check_if_logged_myschedule()


@sign_up_blueprint.route('/signup', methods=["POST", "GET"])
def signup() -> Union[Response, str]:
    if request.method == "POST":
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']
        confirm_password = request.form["password_confirm"]
        flashpop, message = (UserValidator.check_signup_email(email, nickname, password, confirm_password))

        flash(flashpop, message)
        if message == 'warning':
            return redirect(url_for("signup.signup"))

        return redirect(url_for("activation.activation"))

    elif request.method == "GET":
        return check_if_logged_in("signup.html")


@sign_up_blueprint.route('/logout', methods=["POST", "GET"])
def logout() -> Union[Response, str]:
    if "nick" in session:
        session.pop("nick")
        session.pop("email")
        flash("You have been logged out!", "success")
        return redirect(url_for("main.main"))

    flash("You are logged out!", "warning")
    return redirect(url_for("login.login"))


@activation_blueprint.route("/signup/activation", methods=["POST", "GET"])
def activation() -> Union[Response, str]:
    if request.method == "POST":
        email = request.form["email"]
        activation_code = request.form["activation_code"]
        flashpop, message = UserValidator.check_registration(email, activation_code)
        flash(flashpop, message)
        if message == "success":
            return redirect(url_for("login.login"))

        elif message == "warning":
            return render_template("accountactivation.html")

        return redirect(url_for("signup.signup"))



    elif request.method == "GET":
        return check_if_logged_in('accountactivation.html')


@my_account_blueprint.route("/myaccount", methods=["GET"])
def myaccount():
    if request.method == "GET":
        return check_if_logged_in_account_options("accountoptions.html")


@my_account_blueprint.route("/myaccount/changepassword", methods=["POST", "GET"])
def change_password():
    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        new_password_confirm = request.form["new_password_confirm"]
        flashpop, message = UserValidator.handle_change_password(current_password, new_password, new_password_confirm)
        flash(flashpop, message)
        if message == "success":
            return redirect(url_for("signup.logout"))

        return render_template("passwordchange.html")




    elif request.method == "GET":
        return check_if_logged_in_account_options("passwordchange.html")


@my_account_blueprint.route("/myaccount/deleteaccount", methods=["POST", "GET"])
def delete_account():
    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["password_confirm"]
        flashpop, message = UserValidator.handle_account_delete(password, confirm_password)
        flash(flashpop, message)
        if message == "success":
            return redirect(url_for("signup.logout"))
        return render_template("accountdelete.html")




    elif request.method == "GET":
        return check_if_logged_in_account_options("accountdelete.html")



@password_recovery_blueprint.route("/passwordrecovery", methods=["POST", "GET"])
def password_recovery():
    if request.method == "POST":
        email = request.form["email"]
        flashpop, message = UserValidator.handle_password_recovery(email)
        flash(flashpop, message)
        if message == "success":
            user = Users.query.filter_by(email=email).first()
            mail = MailHandler()
            mail.create_reset_email(user)
            return redirect(url_for("login.login"))

        return render_template("passwordrecovery.html")

    elif request.method == "GET":
        return check_if_logged_in("passwordrecovery.html")

@reset_token_blueprint.route("/reset_password/<token>", methods= ["GET", "POST"])
def reset_token(token):
    if request.method == "POST":
        user = Users.verify_reset_token(token)
        handle_token_status(user)
        new_password = request.form["new_password"]
        new_password_confirm = request.form["new_password_confirm"]
        flashpop, message, hashed_password = UserValidator.handle_password_recovery_after_token(new_password, new_password_confirm)
        flash(flashpop,message)
        if message == "success":
            user.password_hash = hashed_password
            db.session.commit()
            return redirect(url_for("login.login"))

        return render_template("resettoken.html")

    elif request.method == "GET":
        return check_if_logged_in("resettoken.html")

def handle_token_status(user:Users):
    if not user:
        flash("Invalid or expired token", "warning")
        return redirect(url_for("password_recovery.password_recovery"))