"""MODULE: access_request. Contains the access request class"""
import json
import hashlib
from .access_manager_config import JSON_FILES_PATH
from .access_management_exception import AccessManagementException
from .data.attributes.email_attribute import Email


class AccessRequest:
    """Class representing the access request"""
    def __init__( self, id_document, full_name, visitor_type, email_address, validity):
        self.__id_document = id_document
        self.__name = full_name
        self.__visitor_type = visitor_type
        self.__email_address = Email(email_address).value
        self.__validity = validity
        #justnow = datetime.utcnow()
        #self.__time_stamp = datetime.timestamp(justnow)
        #only for testing , fix de time stamp to this value 1614962381.90867 , 5/3/2020 18_40
        self.__time_stamp = 1614962381.90867

    def __str__(self):
        return "AccessRequest:" + json.dumps(self.__dict__)

    @property
    def name( self ):
        """Property representing the name and the surname of
        the person who request access to the building"""
        return self.__name
    @name.setter
    def name(self, value):
        """name setter"""
        self.__name = value

    @property
    def visitor_type(self):
        """Property representing the type of visitor: Resident or Guest"""
        return self.__visitor_type
    @visitor_type.setter
    def visitor_type(self, value):
        self.__visitor_type = value

    @property
    def email_address(self):
        """Property representing the requester's email address"""
        return self.__email_address
    @email_address.setter
    def email_address(self, value):
        self.__email_address = value

    @property
    def id_document( self ):
        """Property representing the requester's DNI"""
        return self.__id_document
    @id_document.setter
    def id_document( self, value ):
        self.__id_document = value

    @property
    def validity(self):
        return self.__validity

    @property
    def time_stamp(self):
        """Read-only property that returns the timestamp of the request"""
        return self.__time_stamp

    @property
    def access_code (self):
        """Property for obtaining the access code according the requirements"""
        return hashlib.md5(self.__str__().encode()).hexdigest()

    @staticmethod
    def read_credentials():
        """Returns the list of AccessRequests from the store"""
        json_data = JSON_FILES_PATH + "storeRequest.json"
        try:
            with open(json_data, "r",encoding="utf-8", newline="") as file:
                data = json.load(file)
        except FileNotFoundError as ex:
            raise AccessManagementException("Wrong file or file path") from ex
        except json.JSONDecodeError as ex:
            raise AccessManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return data

    def add_credentials(self):
        """Save the access requests in hte store"""
        json_data = JSON_FILES_PATH + "storeRequest.json"
        try:
            #if file is not exist store the first item
            with open(json_data, "x", encoding="utf-8", newline="") as file:
                data = [self.__dict__]
                json.dump(data, file, indent=2)
        except FileExistsError as ex:
            # if file exists read the file and add a new item
            credentials_data = self.read_credentials()
            # check if this DNI is not stored
            self.check_stored_dni(credentials_data, ex, json_data)

    def check_stored_dni(self, credentials_data, ex, json_data):
        for dni_data in credentials_data:
            if dni_data["_AccessRequest__id_document"] == self.id_document:
                raise AccessManagementException("id_document found in storeRequest") from ex
        credentials_data.append(self.__dict__)
        with open(json_data, "w", encoding="utf-8", newline="") as file:
            json.dump(credentials_data, file, indent=2)
