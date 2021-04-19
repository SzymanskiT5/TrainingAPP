from __future__ import annotations
from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Training(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(length=5000), nullable=True)

    def __init__(self, name: str, date: datetime, duration: int, note: str) -> None:
        self.name = name
        self.date = date
        self.duration = duration
        self.note = note

    def update(self, modified_training: Training) -> None:
        self.name = modified_training.name
        self.date = modified_training.date
        self.duration = modified_training.duration
        self.note = modified_training.note
