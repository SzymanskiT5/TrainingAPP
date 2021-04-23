import sys

from flask import render_template, redirect, url_for, Blueprint, request, session, flash, Response, current_app
from . import db
from .uservalidator import UserValidator
from typing import Union
from .models import Training
from datetime import date

main_blueprint = Blueprint('main', __name__)
login_blueprint = Blueprint('login', __name__)
my_schedule_blueprint = Blueprint('myschedule', __name__)
sign_up_blueprint = Blueprint("signup", __name__)
logout_blueprint = Blueprint("logout", __name__)
registration_blueprint = Blueprint("registration", __name__)

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


def check_if_logged_myschedule() -> Union[Response, str]:
    if "nick" in session:
        return render_template("myschedule.html", events=events)
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
        return render_template("myschedule.html", events=events)

    elif request.method == "GET":
        return check_if_logged_myschedule()


@sign_up_blueprint.route('/signup', methods=["POST", "GET"])
def signup() -> Union[Response, str]:
    if request.method == "POST":
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']
        flashpop, message = (UserValidator.check_signup_email(email, nickname, password))

        flash(flashpop, message)
        if message == 'warning':
            return redirect(url_for("signup.signup"))

        return redirect(url_for("registration.registration"))

    elif request.method == "GET":
        return check_if_logged_in("signup.html")


@sign_up_blueprint.route('/logout', methods=["POST", "GET"])
def logout() -> Union[Response, str]:
    if "nick" in session:
        session.pop("nick")
        session.pop("email")
        flash("You have been logged out!", "success")
        return redirect(url_for("main.main"))

    flash("You are not logged in!", "warning")
    return redirect(url_for("login.login"))


@registration_blueprint.route("/registration", methods=["POST", "GET"])
def registration() -> Union[Response, str]:
    if request.method == "POST":
        email = request.form["email"]
        activation_code = request.form["activation_code"]
        flashpop, message = UserValidator.check_registration(email, activation_code)
        if message == "success":
            flash(flashpop, message)
            return redirect(url_for("login.login"))

        elif message == "warning":
            flash(flashpop, message)
            return render_template("registration.html")
        flash(flashpop, message)

        return redirect(url_for("signup.signup"))



    elif request.method == "GET":
        return check_if_logged_in('registration.html')
