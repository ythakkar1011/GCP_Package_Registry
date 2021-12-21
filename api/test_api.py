import unittest
import main as tasks
import json
import ast

import pyrebase
from flask import Flask, jsonify
from flask_restful import Api, Resource, request

config = {
  "apiKey": "AIzaSyAgpUJ9lfto0Qn3WX4T_BO6Hp458yWDB2o",
  "authDomain": "test-ae93d.firebaseapp.com",
  "databaseURL": "https://test-ae93d-default-rtdb.firebaseio.com/",
  "storageBucket": "test-ae93d.appspot.com"
}

firebase = pyrebase.initialize_app(config)
app = Flask(__name__)
# db = firebase.database()
auth = firebase.auth()
api=Api(app)

class TestSuite(unittest.TestCase): 
    #We have hardcoded the API responses FOR NOW and we will be testing to
    # ensure that the data responses and types are as expected.
    
    def test_packageRetrieve(self):
        with app.test_client() as client:
            #Testing invalid credentials:
            print("Running Bad Credential Test...")
            bad_case = tasks.packageRetrieve(0)
            status_code = bad_case._status_code
            self.assertEqual(401, status_code)
            response_code = ast.literal_eval(bad_case.response[0].decode("utf-8"))['code']
            self.assertEqual(401, response_code)
            response_message = ast.literal_eval(bad_case.response[0].decode("utf-8"))['message']
            self.assertEqual('Error!  You do not have the permissions to view this item!', response_message)

            yield client

        with self.client as client:
            #Test successful retrieval
            print("Running Good Credential Test...")
            successful = tasks.packageRetrieve(0)
            print("-------------------------------------------------------")
            print("*******************************************************")
            print(f"The returned status code was: {successful.status_code}")
            print("*******************************************************")
            print("-------------------------------------------------------")
            self.assertEqual(200, successful.status_code)
            yield client

        # with app.test_client() as client:
        #     #
        #     yield client

        return

    def test_updatePackageVersion(self):
        #Testing invalid credentials:
        with app.test_client() as client:
            bad_case = tasks.updatePackageVersion(0)
            status_code = bad_case._status_code
            self.assertEqual(401, status_code)
            response_code = ast.literal_eval(bad_case.response[0].decode("utf-8"))['code']
            self.assertEqual(401, response_code)
            response_message = ast.literal_eval(bad_case.response[0].decode("utf-8"))['message']
            self.assertEqual('Error!  You do not have the permissions to view this item!', response_message)
            
            yield client

        return
    
    def test_deletePackageVersion(self):
        #Testing invalid credentials:
        with app.test_client() as client:
            bad_case = tasks.deletePackageVersion(0)
            status_code = bad_case._status_code
            self.assertEqual(401, status_code)
            response_code = ast.literal_eval(bad_case.response[0].decode("utf-8"))['code']
            self.assertEqual(401, response_code)
            response_message = ast.literal_eval(bad_case.response[0].decode("utf-8"))['message']
            self.assertEqual('Error!  You do not have the permissions to view this item!', response_message)
            
            yield client

        return

    def test_ratePackage(self):
        #Testing invalid credentials:
        with app.test_client() as client:
            bad_case = tasks.ratePackage(0)
            status_code = bad_case._status_code
            self.assertEqual(401, status_code)
            response_code = ast.literal_eval(bad_case.response[0].decode("utf-8"))['code']
            self.assertEqual(401, response_code)
            response_message = ast.literal_eval(bad_case.response[0].decode("utf-8"))['message']
            self.assertEqual('Error!  You do not have the permissions to view this item!', response_message)
            
            yield client

        return

    def test_resetRegistry(self):
        #Testing invalid credentials:
        with app.test_client() as client:
            bad_case = tasks.resetRegistry()
            status_code = bad_case._status_code
            self.assertEqual(401, status_code)
            response_code = ast.literal_eval(bad_case.response[0].decode("utf-8"))['code']
            self.assertEqual(401, response_code)
            response_message = ast.literal_eval(bad_case.response[0].decode("utf-8"))['message']
            self.assertEqual('You do not have permission to reset the registry.', response_message)
            
            yield client

        return

    def test_getPackages(self):
        #Testing invalid credentials:
        with app.test_client() as client:
            bad_case = tasks.getPackages()
            status_code = bad_case._status_code
            self.assertEqual(401, status_code)
            response_code = ast.literal_eval(bad_case.response[0].decode("utf-8"))['code']
            self.assertEqual(401, response_code)
            response_message = ast.literal_eval(bad_case.response[0].decode("utf-8"))['message']
            self.assertEqual('You do not have permission to view the registry.', response_message)
            
            yield client

        return

    def test_createPackage(self):
        #Testing invalid credentials:
        with app.test_client() as client:
            bad_case = tasks.createPackage()
            status_code = bad_case._status_code
            self.assertEqual(401, status_code)
            response_code = ast.literal_eval(bad_case.response[0].decode("utf-8"))['code']
            self.assertEqual(401, response_code)
            response_message = ast.literal_eval(bad_case.response[0].decode("utf-8"))['message']
            self.assertEqual('You do not have permission to add to the registry.', response_message)
            
            yield client

        return
    
    def test_getPackageByName(self):
        #Testing invalid credentials:
        with app.test_client() as client:
            bad_case = tasks.getPackageByName("test")
            status_code = bad_case._status_code
            self.assertEqual(401, status_code)
            response_code = ast.literal_eval(bad_case.response[0].decode("utf-8"))['code']
            self.assertEqual(401, response_code)
            response_message = ast.literal_eval(bad_case.response[0].decode("utf-8"))['message']
            self.assertEqual('You do not have permission to view the package.', response_message)
            
            yield client

        return
    
    def test_deletePackageVersions(self):
        #Testing invalid credentials:
        with app.test_client() as client:
            bad_case = tasks.deletePackageVersions("test")
            status_code = bad_case._status_code
            self.assertEqual(401, status_code)
            response_code = ast.literal_eval(bad_case.response[0].decode("utf-8"))['code']
            self.assertEqual(401, response_code)
            response_message = ast.literal_eval(bad_case.response[0].decode("utf-8"))['message']
            self.assertEqual('You do not have permission to modify the package.', response_message)
            
            yield client

        return


    
# pytest --cov-report term --cov=. test_api.py --cov-report=html
# or
# pytest test_api.py

from flask import Flask, jsonify
app = Flask(__name__)
def convertJSONFormat(code, data):
    response = app.response_class(
        response=json.dumps(data),
        status=code,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    
    unittest.main()
    exit(0)