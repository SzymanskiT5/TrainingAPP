import os

EMAIL_PATTERN = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
PASSWORD_PATTERN = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
DATE_YYYY_MM_DD_PATTERN = "^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$"
EMAIL_USER = os.getenv("EMAIL_USER")  # <-- Add your email
EMAIL_PASS = os.getenv("EMAIL_PASS")  # <-- Add your email password
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")  # <-- Add your site key
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")  # <-- Add your secret key
