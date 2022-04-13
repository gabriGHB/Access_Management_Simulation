"""Module """
import re
import json
from datetime import datetime

from .access_management_exception import AccessManagementException
from .access_key import AccessKey
from .access_request import AccessRequest
from .access_manager_config import JSON_FILES_PATH
from .data.attributes.email_attribute import Email

class AccessManager:
    """Class for providing the methods for managing the access to a building"""
    def __init__(self):
        pass


    def validate_dni(self,dni):
        self.validate_dni_syntax(dni)
        return self.validate_dni_character(dni)

    def validate_dni_character(self, dni):
        """RETURN TRUE IF THE DNI IS RIGHT, OR FALSE IN OTHER CASE"""
        letters_dni = {"0": "T", "1": "R", "2": "W", "3": "A", "4": "G", "5": "M",
                       "6": "Y", "7": "F", "8": "P", "9": "D", "10": "X", "11": "B",
                       "12": "N", "13": "J", "14": "Z", "15": "S", "16": "Q", "17": "V",
                       "18": "H", "19": "L", "20": "C", "21": "K", "22": "E"}
        numbers_dni = int(dni[0:8])
        module_dni = str(numbers_dni % 23)
        return dni[8] == letters_dni[module_dni]

    @staticmethod
    def validate_dni_syntax(dni):
        """validating the dni syntax"""
        regex_dni = r'^[0-9]{8}[A-Z]{1}$'
        if re.fullmatch(regex_dni, dni):
            return True
        raise AccessManagementException("DNI is not valid")

    @staticmethod
    def validate_validity_days(days, access_type):
        """validating the validity days"""
        if not isinstance(days, int):
            raise AccessManagementException("days invalid")
        if (access_type == "Resident" and days == 0) or (access_type == "Guest" and days >= 2 and days <= 15):
            return True
        raise AccessManagementException("days invalid")

    @staticmethod
    def validate_access_code(access_code):
        """Validating the access code syntax"""
        regex_access_code = '[0-9a-f]{32}'
        if re.fullmatch(regex_access_code, access_code):
            return True
        raise AccessManagementException("access code invalid")

    @staticmethod
    def validate_key_labels(label_list):
        """checking the labels of the input json file"""
        print(label_list.keys())
        if not ("AccessCode" in label_list.keys()):
            raise AccessManagementException("JSON Decode Error - Wrong label")
        if not ("DNI" in label_list.keys()):
            raise AccessManagementException("JSON Decode Error - Wrong label")
        if not ("NotificationMail" in label_list.keys()):
            raise AccessManagementException("JSON Decode Error - Wrong label")
        return True

    @staticmethod
    def read_key_file(keys_file):
        """read the list of stored elements"""
        try:
            with open(keys_file, "r", encoding="utf-8", newline="") as file:
                data = json.load(file)
        except FileNotFoundError as ex:
            raise AccessManagementException("Wrong file or file path") from ex
        except json.JSONDecodeError as ex:
            raise AccessManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return data

    def request_access_code (self, id_card, name_surname, access_type, email_address, days):
        """ this method give access to the building"""
        self.validate_type_syntax(access_type, days)
        self.validate_full_name_syntax(name_surname)
        if self.validate_dni(id_card):
            my_request = AccessRequest(id_card, name_surname, access_type, email_address, days)
            my_request.add_credentials()
            return my_request.access_code
        else:
            raise AccessManagementException("DNI is not valid")

    def validate_full_name_syntax(self, name_surname):
        regex_full_name = r'^[A-Za-z0-9]+(\s[A-Za-z0-9]+)+'
        if not re.fullmatch(regex_full_name, name_surname):
            raise AccessManagementException("Invalid full name")

    def validate_type_syntax(self, access_type, days):
        regex_type = r'(Resident|Guest)'
        if not re.fullmatch(regex_type, access_type):
            raise AccessManagementException("type of visitor invalid")
        self.validate_validity_days(days, access_type)

    def get_access_key(self, keyfile):
        key_file_data = self.read_key_file(keyfile)
        #check if all labels are correct
        self.validate_values_access_key(key_file_data)
        # if everything is ok , generate the key
        dni = AccessKey(key_file_data["DNI"], key_file_data["AccessCode"],
                           key_file_data["NotificationMail"])
        # store the key generated.
        dni.store_keys()
        return dni.key


    def validate_values_access_key(self, key_file_data):
        self.validate_key_labels(key_file_data)
        # check if the values are correct
        self.validate_dni_syntax(key_file_data["DNI"])
        self.validate_access_code(key_file_data["AccessCode"])
        self.validate_email_list(key_file_data)

    def validate_email_list(self, key_file_data):
        num_emails = 0
        for emails in key_file_data["NotificationMail"]:
            num_emails = num_emails + 1
            emails = Email(emails).value
        if num_emails < 1 or num_emails > 5:
            raise AccessManagementException("JSON Decode Error - Email list invalid")
        if not self.validate_dni(key_file_data["DNI"]):
            raise AccessManagementException("DNI is not valid")

    def open_door(self, key):
        self.validate_key_syntax(key)
        key_file_path = JSON_FILES_PATH + "storeKeys.json"
        key_data = self.read_key_file(key_file_path)
        justnow = datetime.utcnow()
        justnow_timestamp = datetime.timestamp(justnow)
        for keys in key_data :
            if keys["_AccessKey__key"] == key \
                    and (keys["_AccessKey__expiration_date"] > justnow_timestamp
                         or keys["_AccessKey__expiration_date"] == 0):
                return True
        raise AccessManagementException("key is not found or is expired")

    def validate_key_syntax(self, key):
        # check if key is complain with the  correct format
        regex_key = r'[0-9a-f]{64}'
        if not re.fullmatch(regex_key, key):
            raise AccessManagementException("key invalid")
