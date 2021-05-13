import re
from datetime import date

from flask import session

from app import db
from app.constans import DATE_YYYY_MM_DD_PATTERN
from app.models import Training
from app.uservalidator import UserValidator


class TrainingHandler:
    """Controlling trainings operations class"""

    @staticmethod
    def get_user_trainings_from_base() -> bool:
        email = session["email"]
        user_id = UserValidator.get_id_by_email(email)
        trainings_found = Training.query.filter_by(user_id=user_id)
        trainings_found = trainings_found.all()
        return trainings_found

    @staticmethod
    def add_training(training: Training) -> None:
        db.session.add(training)
        db.session.commit()

    @staticmethod
    def delete_training(training_id) -> None:
        Training.query.filter(Training.id == training_id).delete()
        db.session.commit()

    @staticmethod
    def get_training_id(user_id, start) -> int:
        training = db.session.query(Training).filter(Training.user_id == user_id) \
            .filter(Training.start == start).first()
        training_id = training.id
        return training_id

    @staticmethod
    def check_date_format(date_format) -> date:
        "JS sometimes sends another date format, SQLite has problem with queries, this function is to avoid this."
        if re.match(DATE_YYYY_MM_DD_PATTERN, date_format):
            return date_format
        return Training.reformate_date(date_format)

    @staticmethod
    def update_training(json_body: dict, training_id) -> None:
        training_new = Training.create_from_json(json_body)
        training = db.session.query(Training).filter(Training.id == training_id).first()
        training.update(training_new)
        db.session.commit()
