import os
import smtplib
import sys
from email.message import EmailMessage

from flask import url_for

from app.models import Users


class MailHandler:
    """Using environment variables to make our dates safe"""

    def __init__(self):
        self.email = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")

    def create_activation_email(self, email: str, activation_code: str) -> None:
        msg = EmailMessage()
        msg['Subject'] = "Finish your registration"
        msg["From"] = self.email
        msg["To"] = email
        msg.set_content = ("Registration")
        msg.add_alternative(f"""\
        <!DOCTYPE html>
        <html>
            <body>
                <h1> Finish your registration!</h1>
                <p> Hi! Your code is bellow. After 30 minutes code will be deleted with account. Cheers! </p>
                <h2>{activation_code}</h2>
            </body>
        </html>
        """, subtype='html')

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email, self.password)
            smtp.send_message(msg)

    def create_reset_email(self, user: Users):
        token = user.get_reset_token()
        msg = EmailMessage()
        msg['Subject'] = "Reset your password"
        msg["From"] = self.email
        msg["To"] = user.email
        print(user.email, file=sys.stderr)
        msg.set_content = ("Registration")
        msg.add_alternative(f"""\
                <!DOCTYPE html>
                <html>
                    <body>
                        <h1> Reset your password!</h1>
                        <p> Hi! Click link bellow to reset your password. </p>
                        <h2> {url_for("reset_token.reset_token", token=token, _external=True)}</h2>
                    </body>
                </html>
                """, subtype='html')
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email, self.password)
            smtp.send_message(msg)