from .attribute import Attribute

class Email(Attribute):
    _validation_pattern = r'^[a-z0-9]+[\._]?[a-z0-9]+[@](\w+[.])+\w{2,3}$'
    _error_message = "Email invalid"
