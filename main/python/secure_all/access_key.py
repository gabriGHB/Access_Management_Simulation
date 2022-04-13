"""Contains the class Access Key"""
from datetime import datetime
import hashlib
import json

from .access_manager_config import JSON_FILES_PATH
from .access_management_exception import AccessManagementException
from .data.attributes.access_code_attribute import AccessCode
from .access_request import AccessRequest

class AccessKey():
    """Class representing the key for accessing the building"""

    def __init__(self, dni, access_code, notification_emails):
        self.__alg = "SHA-256"
        self.__type = "DS"
        self.__dni = dni
        self.__access_code = AccessCode(access_code).value
        access_request_stored = self.validate_dni_with_access_code(dni, access_code)
        validity =access_request_stored.validity
        self.__notification_emails = notification_emails
        justnow = datetime.utcnow()
        self.__issued_at = datetime.timestamp(justnow)
        # fix self.__issued_at only for testing 13-3-2021 18_49
        self.__issued_at=1615627129.580297
        if validity == 0:
            self.__expiration_date = 0
        else:
            #timestamp is represneted in seconds.microseconds
            #validity must be expressed in senconds to be added to the timestap
            self.__expiration_date = self.__issued_at + (validity * 30 * 24 * 60 *60)
        self.__key = hashlib.sha256(self.__signature_string().encode()).hexdigest()


    @staticmethod
    def find_credentials(access_request_dni):
        """ return the access request related to a given dni"""
        file_path = JSON_FILES_PATH + "storeRequest.json"
        try:
            with open(file_path, "r", encoding="utf-8", newline="") as file:
                list_data = json.load(file)
        except FileNotFoundError as ex:
            raise AccessManagementException("Wrong file or file path") from ex
        except json.JSONDecodeError as ex:
            raise AccessManagementException("JSON Decode Error - Wrong JSON Format") from ex
        for dni_data in list_data:
            if dni_data["_AccessRequest__id_document"] == access_request_dni:
                return dni_data
        return None


    def validate_dni_with_access_code(self, dni, access_code):
        # check if this dni is stored, and return in dni all the info
        request_stored = self.find_credentials(dni)
        if request_stored is None:
            raise AccessManagementException("DNI is not found in the store")
        access_request_object = AccessRequest(request_stored['_AccessRequest__id_document'],
                                              request_stored['_AccessRequest__name'],
                                              request_stored['_AccessRequest__visitor_type'],
                                              request_stored['_AccessRequest__email_address'],
                                              request_stored['_AccessRequest__validity'])
        if access_request_object.access_code != access_code:
            raise AccessManagementException("access code is not correct for this DNI")
        return access_request_object

    def __signature_string(self):
        """Composes the string to be used for generating the key"""
        return "{alg:"+self.__alg + ",typ:" + self.__type + ",accesscode:"\
               + self.__access_code+",issuedate:"+str(self.__issued_at)\
               + ",expirationdate:" + str(self.__expiration_date) + "}"
    @property
    def expiration_date(self):
        """expiration_date getter"""
        return self.__expiration_date

    @expiration_date.setter
    def expiration_date(self, value):
        """expiration_date setter"""
        self.__expiration_date = value

    @property
    def dni(self):
        """Property that represents the dni of the visitor"""
        return self.dni
    @dni.setter
    def dni(self,value):
        """dni setter"""
        self.__dni = value

    @property
    def access_code(self):
        """Property that represents the access_code of the visitor"""
        return self.__access_code
    @access_code.setter
    def access_code(self, value):
        """access_code setter"""
        self.__access_code = value

    @property
    def notification_emails(self):
        """Property that represents the access_code of the visitor"""
        return self.__notification_emails

    @notification_emails.setter
    def notification_emails( self, value ):
        self.__notification_emails = value

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        self.__key = value

    def store_keys(self):
        """ srote de keys """
        myFile = JSON_FILES_PATH + "storeKeys.json"
        try:
            with open(myFile, "r",encoding="utf-8", newline="") as file:
                list_keys = json.load(file)
            # append the new key
            list_keys.append(self.__dict__)
            # write all the keys in the file
            with open(myFile, "w", encoding="utf-8", newline="") as file:
                json.dump(list_keys, file, indent=2)
        except FileNotFoundError as ex:
            # if file is not found, store the first key
            with open(myFile, "x", encoding="utf-8", newline="") as file:
                data_key = [self.__dict__]
                json.dump(data_key, file, indent=2)
        except json.JSONDecodeError as ex:
            raise AccessManagementException("JSON Decode Error - Wrong JSON Format") from ex
