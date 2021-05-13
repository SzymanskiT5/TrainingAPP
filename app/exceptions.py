class CodeExpired(Exception):
    pass


class WrongCodeOrEmail(Exception):
    pass


class WrongEmailFormat(Exception):
    pass


class EmailExists(Exception):
    pass


class TooLongNick(Exception):
    pass


class NickExists(Exception):
    pass


class FalsePasswordFormat(Exception):
    pass


class EmailRegistrationDoesntExists(Exception):
    pass


class EnteredPasswordIncorrect(Exception):
    pass


class PasswordsAreNotTheSame(Exception):
    pass


class AccountNotActivated(Exception):
    pass


class AccountIsActivated(Exception):
    pass


class RecaptchaIsMissing(Exception):
    pass
