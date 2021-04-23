import os
import smtplib
from email.message import EmailMessage



class MailHandler:
    """Using environment variables to make our dates safe"""

    def __init__(self):
        self.email = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")

    def create_email(self, email: str, activation_code: str) -> None:
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
                <p> "Hi! Your code is {activation_code}    After 30 minutes code will be deleted with account. Cheers!" </p>
            </body>
        </html>
        """, subtype='html')

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email, self.password)
            smtp.send_message(msg)
