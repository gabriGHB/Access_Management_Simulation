from .attribute import Attribute

class AccessCode(Attribute):
    _validation_pattern = '[0-9a-f]{32}'
    _error_message = "access code invalid"
