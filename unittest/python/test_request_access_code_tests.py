""" doc """
import json
import os.path
import unittest
from os import remove
import csv
from secure_all import AccessManager, AccessManagementException, AccessRequest, JSON_FILES_PATH



class MyTestCase(unittest.TestCase):
    """ doc """


    @classmethod
    def setUpClass(cls):
        """ inicializo el entorno de prueba """
        fichero = "storeRequest.json"
        my_file = JSON_FILES_PATH + fichero
        print (my_file)
        if os.path.exists(my_file):
            remove (my_file)

    @staticmethod
    def read_file():
        """ this method read a Json file and return the value """
        my_file= JSON_FILES_PATH + "storeRequest.json"
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
        my_cases = JSON_FILES_PATH + "testingCases_RF1.csv"
        with open(my_cases, newline='', encoding='utf-8') as csvfile:
            param_test_cases = csv.DictReader(csvfile, delimiter=';')
            my_code = AccessManager()
            for row in param_test_cases:
                test_id = row[ 'ID TEST' ]
                dni = row[ "DNI" ]
                name = row[ "NAME SURNAME" ]
                access_type = row[ "ACCESS TYPE" ]
                email = row[ "email" ]
                days = int(row[ "VALIDITY" ])
                result = row[ "EXPECTED RESULT" ]
                valid = row["VALID INVALID"]
                if valid ==  "VALID":
                    print("Param:" + test_id + valid)
                    valor = my_code.request_access_code(dni, name,access_type,email,days)
                    self.assertEqual(result, valor)
                    # Check if this DNI is store in storeRequest.json
                    my_data = self.read_file()
                    my_request = AccessRequest(dni, name,access_type,email,days)
                    found = False
                    for k in my_data:
                        if k[ "_AccessRequest__id_document" ] == dni:
                            found = True
                            # this assert give me more information
                            # about the differences than assertEqual
                            self.assertDictEqual(k, my_request.__dict__)
                    # if found is False , this assert fails
                    self.assertTrue(found)
                else:
                    print("Param:" + test_id + "-" + valid)
                    with self.assertRaises(AccessManagementException) as c_m:
                        my_code.request_access_code(dni, name,access_type,email,days)
                    self.assertEqual(c_m.exception.message, result)

def test_invalid_days_character(self):
    """Testing an character instead of a number for days"""
    my_code = AccessManager()
    with self.assertRaises(AccessManagementException) as c_m:
        my_code.request_access_code("12345678Z", "Pedro Martin", "Resident", "test@test.com", "a")
    self.assertEqual(c_m.exception.message, "days invalid")

if __name__ == '__main__':
    unittest.main()
