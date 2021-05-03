from __future__ import annotations

import sys
from datetime import datetime, date

from flask import session

from app import db, login_manager, app, ma, fields
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from flask_marshmallow import Marshmallow, fields, ma
from flask_login import UserMixin

# from app.uservalidator import UserValidator


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
    name = db.Column(db.String(length=50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(length=5000), nullable=True)
    rate = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users._id"))

    def __init__(self, name: str, date: date, duration: int, note: str, rate: int, user_id: int) -> None:
        self.name = name
        self.date = date
        self.duration = duration
        self.note = note
        self.rate = rate
        self.user_id = user_id

    def __str__(self):
        return f"{self.name},{self.date}, {self.duration}, {self.note}, {self.rate}, {self.user_id}"

    def update(self, modified_training: Training) -> None:
        self.name = modified_training.name
        self.date = modified_training.date
        self.duration = modified_training.duration
        self.note = modified_training.note
        self.rate = modified_training.rate

    @staticmethod
    def create_from_json(json_body: dict) -> Training:
        email = session['email']
        user_id= db.session.query(Users).filter(Users.email == email).first()
        db.session.commit()
        user_id = user_id._id
        date = json_body["date"]
        date = datetime.fromisoformat(date[:-1])
        return Training(name= json_body["name"], date=date, duration=json_body["duration"],
                        note=json_body["note"], rate=json_body["rate"], user_id = user_id)



class TrainingSchema(ma.Schema):
    id = fields.fields.Integer()
    name = fields.fields.Str()
    date = fields.fields.DateTime(format='%Y-%m-%d')
    duration = fields.fields.Integer()
    note = fields.fields.Str()
    rate = fields.fields.Integer()
    user_id = fields.fields.Integer()


