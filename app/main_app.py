from flask import render_template, redirect, url_for, Blueprint, request, session, flash, Response
from . import db
from .uservalidator import UserValidator
from typing import Union
from .models import Training


main_blueprint = Blueprint('main', __name__)
login_blueprint = Blueprint('login', __name__)
my_schedule_blueprint = Blueprint('myschedule', __name__)
sign_up_blueprint = Blueprint("signup", __name__)
logout_blueprint = Blueprint("logout",__name__)

events = [
    {
        "name":" test",
        "date": "2021-04-20",



    }


]

def check_if_logged_in(template_name: str):
    if "nick" in session:
        flash('You are already logged in', 'success')
        return redirect(url_for("main.main"))

    return render_template(template_name)


def check_if_logged_myschedule() -> Union[Response, str]:
    if "nick" in session:
        return render_template("myschedule.html", events =events)
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
def login():
    if request.method == "POST":
        session.permanent = True
        email_or_nick = request.form['nickname']
        password = request.form['password']

        return handle_login(email_or_nick, password)

    elif request.method == "GET":
        return check_if_logged_in("login.html")


@my_schedule_blueprint.route('/myschedule', methods=["POST", "GET"])
def my_schedule():
    if request.method == "POST":
        name = request.form['name']
        date = request.form['date']
        duration = request.form['duration']
        note = request.form['note']
        rate = request.form['rate']
        training = Training(name=name, date=date, duration=duration, note=note, rate=rate, user=session["nick"])
        db.session.add(training)
        db.session.commit()
        flash("Training added!", "success")
        return render_template("myschedule.html", events = events)



    elif request.method == "GET" :
        return check_if_logged_myschedule()


@sign_up_blueprint.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']
        flashpop, message = (UserValidator.check_signup_email(email, nickname, password))

        flash(flashpop, message)
        if message == 'warning':
            return redirect(url_for("signup.signup"))

        return redirect(url_for("main.main"))
    elif request.method == "GET":
        return check_if_logged_in("signup.html")


@sign_up_blueprint.route('/logout', methods=["POST", "GET"])
def logout():
    if "nick" in session:
        session.pop("nick")
        session.pop("email")
        flash("You have been logged out!", "success")
        return redirect(url_for("main.main"))

    flash("You are not logged in!", "warning")
    return redirect(url_for("login.login"))