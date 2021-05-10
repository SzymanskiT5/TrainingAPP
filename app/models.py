from __future__ import annotations

import sys
from datetime import datetime, date
from flask import session
from app import db, login_manager, app, ma, fields
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin




@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(128))
    activation_code = db.Column(db.String(length=8))
    is_activated = db.Column(db.Integer)
    expire_date = db.Column(db.DateTime)
    workouts = db.relationship("Training", backref="user")

    def __init__(self, name: str, email: str, password_hash: str, activation_code: str, is_activated: int,
                 expire_date=datetime):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.activation_code = activation_code
        self.is_activated = is_activated
        self.expire_date = expire_date



    def get_reset_token(self, expire_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expire_sec)
        return s.dumps({"user_id": self._id}).decode("utf-8")

    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)




class Training(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(length=50), nullable=False)
    start = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(length=5000), nullable=True)
    rate = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users._id"))

    def __init__(self, title: str, start: date, duration: int, description: str, rate: int, user_id: int) -> None:
        self.title = title
        self.start = start
        self.duration = duration
        self.description = description
        self.rate = rate
        self.user_id = user_id

    def __str__(self):
        return f"{self.title},{self.start}, {self.duration}, {self.description}, {self.rate}, {self.user_id}"

    def update(self, modified_training: Training) -> None:
        self.title = modified_training.title
        self.duration = modified_training.duration
        self.description = modified_training.description
        self.rate = modified_training.rate

    @staticmethod
    def create_from_json(json_body: dict) -> Training:
        email = session['email']
        user_id= db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        user_id = user_id._id
        start = json_body["start"]
        start = Training.reformate_date(start)
        return Training(title=json_body["title"], start=date.fromisoformat(start), duration=json_body["duration"],
                        description=json_body["description"], rate=json_body["rate"], user_id = user_id)

    @staticmethod
    def reformate_date(start):
        start = start.split(".")
        start.reverse()
        print(start[2], file=sys.stderr)
        if len(start[2]) != 2:
            day = ["0", start[2]]
            start[2] = "".join(day)
        start = "-".join(start)

        print(start, file=sys.stderr)
        return start




class TrainingSchema(ma.Schema):
    id = fields.fields.Integer()
    title = fields.fields.Str()
    start = fields.fields.Date(format='%Y-%m-%d')
    duration = fields.fields.Integer()
    description = fields.fields.Str()
    rate = fields.fields.Integer()


