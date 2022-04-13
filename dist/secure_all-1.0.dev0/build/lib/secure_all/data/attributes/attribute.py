from ...access_management_exception import AccessManagementException
import re

class Attribute():
    _attr_value = ""
    _validation_pattern = ""
    _error_message = ""

    def _validate(self, attr_value):
        if not isinstance(attr_value, str):
            raise AccessManagementException(self._error_message)
        if not re.fullmatch(self._validation_pattern, attr_value):
            raise AccessManagementException(self._error_message)
        return attr_value

    def __init__(self, attr_value):
        self._attr_value = self._validate(attr_value)

    @property
    def value(self):
        return self._attr_value