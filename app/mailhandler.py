import os
import random
import smtplib
from email.message import EmailMessage
import string
from werkzeug.security import generate_password_hash, check_password_hash


class MailHandler:
    """Using enviroment variabels to make our dates safe"""

    def __init__(self):
        self.email = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")



    def create_code_and_add_to_db(self):
        password = ''.join(random.choice(string.printable) for i in range(8))

        return password





    def create_email(self, email):
        msg = EmailMessage()
        msg['Subject'] = "Finish your registration"
        msg["From"] = email
        msg["To"] = email
        msg.set_content = ("TEST")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email, self.password)
            smtp.send_message(msg)


mail = MailHandler()
print(mail.create_code_and_add_to_db())