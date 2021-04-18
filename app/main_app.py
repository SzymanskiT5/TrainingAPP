from flask import render_template, redirect, url_for, Blueprint, request, session, flash
from . import db
from .handler import Handler

main_blueprint = Blueprint('main', __name__)
login_blueprint = Blueprint('login', __name__)
my_schedule_blueprint = Blueprint('myschedule', __name__)
sign_up_blueprint = Blueprint("signup", __name__)
logout_blueprint = Blueprint("logout",__name__)
execute = Handler()


@main_blueprint.route('/', methods=["GET"])
def main():
    return render_template('main.html')


@login_blueprint.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        if "nick" in session:
            flash('You are already logged in', 'success')
            return redirect(url_for("main.main"))

        email_or_nick = request.form['nickname']
        password = request.form['password']

        flashpop, message, nickname, email = execute.check_login(email_or_nick, password)

        if message == 'success':
            session.update({"nick": nickname, "email": email})
            flash(flashpop, message)
            return redirect(url_for("main.main"))

        if message == 'error':
            flash(flashpop, message)
            return render_template("login.html")


    elif request.method == "GET":
        return render_template("login.html")


@my_schedule_blueprint.route('/myschedule', methods=["POST", "GET"])
def my_schedule():
    return "TEST"


@sign_up_blueprint.route('/signup', methods=["POST", "GET"])
def signup():
    if "nick" in session:
        flash("You are already logged in", "success")
        return redirect(url_for("my_schedule.my_schedule"))

    elif request.method == "POST":
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']
        flashpop, message = (execute.check_signup_email(email, nickname, password))
        if message == 'warning':
            flash(flashpop, message)
            return redirect(url_for("signup.signup"))
        else:
            flash(flashpop, message)
            return redirect(url_for("main.main"))



    elif request.method == "GET":
        return render_template("signup.html")

@sign_up_blueprint.route('/logout', methods=["POST", "GET"])
def logout():
    if "nick" in session:
        session.pop("nick")
        session.pop("email")
        flash("You have been logged out!", "success")
        return redirect(url_for("main.main"))

    flash("You are not logged in!", "warning")
    return redirect(url_for("login.login"))