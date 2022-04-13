"""Test module for testing get_access_key"""
import os
import unittest
import csv
import json

from secure_all import AccessManager, AccessManagementException, JSON_FILES_PATH


class TestAccessManager(unittest.TestCase):
    """Test class for testing get_access_key"""

    @classmethod
    def setUpClass(cls) -> None:
        """Removing the Stores and creating required AccessRequest for testing"""
        cls.set_up_store_keys()
        cls.set_up_store_request()
        # introduce a key valid and not expired and guest
        my_manager = AccessManager()
        my_manager.request_access_code("05270358T", "Pedro Martin",
                                            "Resident", "uc3m@gmail.com", 0)

        my_manager.request_access_code("87654123L", "Maria Montero",
                                            "Guest", "maria@uc3m.es", 15)

        my_manager.request_access_code("53935158C", "Marta Lopez",
                                                "Guest", "uc3m@gmail.com", 5)

    @classmethod
    def set_up_store_request(cls):
        fichero_keys = "storeRequest.json"
        my_file = JSON_FILES_PATH + fichero_keys
        if os.path.exists(my_file):
            os.remove(my_file)

    @classmethod
    def set_up_store_keys(cls):
        fichero_keys = "storeKeys.json"
        my_file = JSON_FILES_PATH + fichero_keys
        if os.path.exists(my_file):
            os.remove(my_file)

    @staticmethod
    def read_file():
        """ this method read a Json file and return the value """
        my_file = JSON_FILES_PATH + "storeKeys.json"
        try:
            with open(my_file, "r", encoding="utf-8", newline="") as file:
                data = json.load(file)
        except FileNotFoundError as ex:
            raise AccessManagementException("Wrong file or file path") from ex
        except json.JSONDecodeError as ex:
            raise AccessManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return data

    def test_parametrized_cases_tests( self ):
        """Parametrized cases read from testingCases_RF1.csv"""
        my_cases = JSON_FILES_PATH + "testingCases_RF2.csv"
        with open(my_cases, newline='', encoding='utf-8') as csvfile:
            param_test_cases = csv.DictReader(csvfile, delimiter=';')
            my_code = AccessManager()
            for row in param_test_cases:
                test_id = row[ 'ID TEST' ]
                result = row[ "EXPECTED RESULT" ]
                valid = row["VALID INVALID"]
                file_name = JSON_FILES_PATH + row["FILE"]
                if valid ==  "VALID":
                    print("Param:" + test_id + valid)
                    valor = my_code.get_access_key(file_name)
                    self.assertEqual(result, valor)
                    list_keys = self.read_file()
                    found = False
                    for the_key in list_keys:
                        if the_key["_AccessKey__key"] == valor:
                            found = True
                    self.assertTrue(found)
                else:
                    print("Param:" + test_id + "-" + valid)
                    with self.assertRaises(AccessManagementException) as c_m:
                        my_code.get_access_key(file_name)
                    self.assertEqual(c_m.exception.message, result)

if __name__ == '__main__':
    unittest.main()
