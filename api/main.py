import json
import datetime
import jwt
import pyrebase
import base64
from flask import Flask, jsonify
from flask_restful import Api, Resource, request
from google.cloud import firestore

import main_rate as rate

# config = {
#   "apiKey": "AIzaSyAgpUJ9lfto0Qn3WX4T_BO6Hp458yWDB2o",
#   "authDomain": "test-ae93d.firebaseapp.com",
#   "databaseURL": "https://test-ae93d-default-rtdb.firebaseio.com/",
#   "storageBucket": "test-ae93d.appspot.com"
# }

config = {
  "apiKey": "AIzaSyCww7v821615HnWe-2oEzbmMZzVFbZHBWM",
  "authDomain": "lexical-botany-331616.firebaseapp.com",
  "databaseURL": "https://lexical-botany-331616-default-rtdb.firebaseio.com/",
  "storageBucket": "lexical-botany-331616.appspot.com"
}
firebase = pyrebase.initialize_app(config)
app = Flask(__name__)
# db = firebase.database()
auth = firebase.auth()
api=Api(app)
"""
Begin helper functions:
"""
def convertJSONFormat(code, data):
    response = app.response_class(
        response=json.dumps(data),
        status=code,
        mimetype='application/json'
    )
    return response

def checkAuth():
    #Get & process authentification
    # auth_token = request.headers.get('X-Authorization').split()[1]
    auth_token = ''
    userFound = False
    header_tuples = request.headers
    # print(header_tuples)
    for i in header_tuples:
        if 'X-Authorization' in i:
            auth_token = i[1]
    # auth_token = json.loads(auth_token)
    # print(auth_token)

    try:
        #Check permissions:
        #   1. Search db of Users with auth_token as filter:
        # print("try started")
        db = firebase.database()
        auth_validation = db.child("Users").get()
        for i in auth_validation.val():
            if auth_validation.val()[i]['Token'] == auth_token:
                userName = auth_validation.val()[i]['User']['name']
                isUserAdmin = auth_validation.val()[i]['User']['isAdmin']
                userFound = True
                

        if userFound:
            return [1, userName, isUserAdmin]
    except Exception:
        return [0, None, None]

#     try:
#         #Check permissions:
#         #   1. Search db of Users with auth_token as filter:
#         db = firebase.database()
#         auth_validation = db.child("User").order_by_child("Token").equal_to(auth_token)
#         #   2. Get results & return if the query yields any Users
#         return len(list(auth_validation.fetch()))
#     except Exception:
#         return 0

"""
/package/<id> URLS:
"""
@app.route("/package/<id>", methods=['GET'])
def packageRetrieve(id):
    try:
        checkValues = []
        returnData = []
        checkValues = checkAuth()
        request.get_data()
        if checkValues:
            if checkValues[0] == 0:
                return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to modify the package.'})
        else:
            return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
        # request.get_data()
        
        # if(checkAuth() == 0): 
        #     return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to view the package.'})

        db = firebase.database()
        packageNotFound = 1

        try:
            #Query for all packages:
            # packages = db.child("package").order_by_child("Name").equal_to(name).get()
            for packageKey in db.child("Packages").get().val():
                # print(packageKey)
                # print(name)
                # print(db.child("Packages").child(packageKey).get().val())
                # for actions in db.child("Packages").child(packageKey).get().val():
                    # print(actions)
                if db.child("Packages").child(packageKey).get().val()['Metadata']['ID'] == id:
                    # print("Reached here")
                    newData = {'Download' : {'User':{'name': checkValues[1], 'isAdmin': checkValues[2]},'Date': f"{datetime.datetime.now()}",'PackageMetadata': db.child("Packages").child(packageKey).get().val()['Metadata'],'Action': "Download"}}
                    db.child("Packages").child(packageKey).update(newData)
                    packageNotFound = 0
                    for actions in db.child("Packages").child(packageKey).get().val():
                        # print(actions)
                        if actions != 'Metadata' and actions != 'packageData':
                            # print(actions)
                            data = db.child("Packages").child(packageKey).child(actions).get().val()
                            returnData.append(data)
                        # print(returnData)
                    return convertJSONFormat(200, returnData)
            if packageNotFound:            
                return convertJSONFormat(400, {'code': 400, 'message': 'No such package.'})
        except Exception:
            return convertJSONFormat(400, {'code': 400, 'message': 'Error in retrieving package.'})
    except Exception:
        return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
    # try:
    #     request.get_data()    

    #     if(checkAuth() == 0): 
    #         return convertJSONFormat(401, {'code': 401, 'message': 'Error!  You do not have the permissions to view this item!'})

    #     db = firebase.database()
        
    #     try:
    #         results = db.child("package").order_by_child("ID").equal_to(id).get()
    #         if(list(results) != []):
    #             #Query for package by ID
    #             pack = results.get(results.key('package', id))

    #             api_response = {
    #                 'metadata': {
    #                         'Name': pack['Name'],
    #                         'Version': pack['Version'],
    #                         'ID': pack['ID']
    #                     },
    #                     'data': {
    #                         'Content': pack['Content'],
    #                         'URL': pack['URL'],
    #                         'JSProgram': pack['JSProgram']
    #                     }   
    #                 }
    #             return convertJSONFormat(200, api_response)
    #     except Exception:
    #         pass

    #     return convertJSONFormat(400, {'code': 400, 'message': 'Error! Something went wrong when processing your request!  Please ensure that your request was made properly!'})
    # except Exception:
    #     return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})


@app.route("/package/<id>", methods=['PUT'])
def updatePackageVersion(id):
    try:
        packageURL = None
        packageContent = None
        checkValues = []
        checkValues = checkAuth()
        request.get_data()
        if checkValues:
            if checkValues[0] == 0:
                return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to add to the registry.'})
        else:
            return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})

        currentUserName = checkValues[1]
        currentIsAdmin = checkValues[2]


        # if(checkAuth() == 0): 
        #     return convertJSONFormat(401, {'code': 401, 'message': 'Error!  You do not have the permissions to view this item!'})

        #Load Request Body as JSON:
        req_body = json.loads(request.data.decode('utf-8'))

        #Parse Data as metadata and data:
        try:
            metadata = req_body['metadata']
            data = req_body['data']
        except Exception:
            return convertJSONFormat(400, {'code': 400, 'message': 'Malformed request (e.g. no such package).'})
        
        db = firebase.database()
        packageNotFound = 1

        #Check that Metadata matches URL
        try:
            if(id == metadata['ID']):
                #Select from database to make sure package exists:
                for packageKey in db.child("Packages").get().val():
                    # print(db.child("Packages").child(packageKey).get().val()['Metadata']['Name'])
                    if db.child("Packages").child(packageKey).get().val()['Metadata']['Name'] == metadata['Name'] and db.child("Packages").child(packageKey).get().val()['Metadata']['ID'] == metadata['ID'] and db.child("Packages").child(packageKey).get().val()['Metadata']['Version'] == metadata['Version']:
                        # print("reached here")
                        packageNotFound = 0
                        db.child("Packages").child(packageKey).child("packageData").remove()
                        db.child("Packages").child(packageKey).child("packageData").set(data)
                        newData = {'Update' : {'User':{'name': currentUserName, 'isAdmin': currentIsAdmin},'Date': f"{datetime.datetime.now()}",'PackageMetadata': metadata,'Action': "Update"}}
                        db.child("Packages").child(packageKey).update(newData)
                        return convertJSONFormat(200, {'code' : 200, 'message': 'Package Updated'})
                
                if packageNotFound:
                    return convertJSONFormat(400, {'code' : 400, 'message': 'Something went wrong with updating'})

                #Add filters for name...
                # search.order_by_child("Name").equal_to(metadata["Name"])
                # #...and version (specified as a unique identifier pair)
                # search.order_by_child("Version").equal_to(metadata["Version"])

                # if(list(search.get()) != []): #If this is a valid (existing) identifier pair:
                #     #Get most recent package:
                #     former_version = search
                #     former_version.order_by_child("package").equal_to(id).get()
                #     #Remove most recent package:
                #     former_version.remove()

                    #Update with newest version with metadata and data info:
                    # package_payload = {
                    #     'metadata':{
                    #         'Name': metadata['Name'],
                    #         'Version': metadata['Version'],
                    #         'ID': metadata['ID']
                    #     },
                    #     'data':{
                    #         'Content': data['Content'],
                    #         'URL': data['URL'],
                    #         'JSProgram': data['JSProgram']
                    #     }
                    # }

                    #Add to database:
                    # db.child("package").set(package_payload)
                    
        except Exception:
            pass

        return convertJSONFormat(400, {'code' : 400, 'message': 'Malformed request (e.g. no such package).'})
    except Exception:
        return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})

@app.route("/package/<id>", methods=['DELETE'])
def deletePackageVersion(id):
    try:
        checkValues = []
        checkValues = checkAuth()
        request.get_data()
        if checkValues:
            if checkValues[0] == 0:
                return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to modify the package.'})
        else:
            return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
        
        # if(checkAuth() == 0): 
        #     return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission '})

        db = firebase.database()
        packageNotFound = 1

        #Try Deleting the package:
        try:
            for packageKey in db.child("Packages").get().val():
                # print(packageKey)
                # print(db.child("Packages").get().val()[packageKey])
                if db.child("Packages").child(packageKey).get().val()['Metadata']['ID'] == id:
                    # print("Package Removed")
                    packageNotFound = 0
                    db.child("Packages").child(packageKey).remove()
                    return convertJSONFormat(200, {'code': 200, 'message': 'Package is deleted.'})
            if packageNotFound:
                return convertJSONFormat(400, {'code': 400, 'message': 'No such package.'})
        except Exception:
            return convertJSONFormat(400, {'code': 400, 'message': 'Error in retrieving package for deletion.'})

        # if(list(packages.get())==[]):
        #     return convertJSONFormat(400, {'code': 400, 'message': 'No such package.'})
        # try:
        #     packages.remove()
        #     return convertJSONFormat(200, {'code': 200, 'message': 'Package is deleted.'})
        # except Exception:
        #     return convertJSONFormat(400, {'code': 400, 'message': 'Error in deleting package.'})
    except Exception:
        return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
    # try:
    #     request.get_data()
        
    #     if(checkAuth() == 0): 
    #         return convertJSONFormat(401, {'code': 401, 'message': 'Error!  You do not have the permissions to delete this item!'})
        
    #     db = firebase.database()

    #     try:
    #         #Query packages to find package {id}
    #         results = db.child("package").order_by_child("ID").equal_to(id)
    #         if(list(results.get()) != []):
    #             #Delete package by ID:
    #             results.remove()
    #             return convertJSONFormat(200, {'code': 200, 'message': 'Package is deleted.'})
    #     except Exception:
    #         pass

    #     return convertJSONFormat(400, {'code': 400, 'message':'No such package.'})
    # except Exception:
    #     return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})

@app.route("/package/<id>/rate", methods=['GET'])
def ratePackage(id):
    try:
        checkValues = []
        checkValues = checkAuth()
        request.get_data()
        if checkValues:
            if checkValues[0] == 0:
                return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to modify the package.'})
        else:
            return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
        
        currentUserName = checkValues[1]
        currentIsAdmin = checkValues[2]
        # request.get_data()

        # if(checkAuth() == 0): 
        #     return convertJSONFormat(401, {'code': 401, 'message': 'Error!  You do not have the permissions to view this item!'})

        db = firebase.database()
        packageFound = 0
        # results = db.child("package").order_by_child("ID").equal_to(id)
        try:
            #Query for all packages:
            # packages = db.child("package").order_by_child("Name").equal_to(name).get()
            for packageKey in db.child("Packages").get().val():
                # print(packageKey)
                if db.child("Packages").child(packageKey).get().val()['Metadata']['ID'] == id:
                    # print("Reached Here")
                    
                    if 'URL' in db.child("Packages").child(packageKey).get().val()['packageData']:
                        packageFound = 1
                        try:
                            # netScore, rampUpScore, correctnessScore, busFactorScore, responsiveMaintainerScore, licenseScore = rate.call_main(db.child("Packages").child(packageKey).get().val()['packageData']['URL'])
                            packageRating = rate.call_main(db.child("Packages").child(packageKey).get().val()['packageData']['URL'])
                            # print(packageRating)
                            metadata = db.child("Packages").child(packageKey).get().val()['Metadata']
                            api_response = {'RampUp': packageRating[1],'Correctness': packageRating[2],'BusFactor': packageRating[3],'ResponsiveMaintainer': packageRating[4],'LicenseScore': packageRating[5],'GoodPinningPractice': packageRating[6]}
                            newData = {'Rate' : {'User':{'name': currentUserName, 'isAdmin': currentIsAdmin},'Date': f"{datetime.datetime.now()}",'PackageMetadata': metadata,'Action': "Rate"}}
                            db.child("Packages").child(packageKey).update(newData)
                            return convertJSONFormat(200, api_response)
                        except Exception:
                            return convertJSONFormat(500, {'code': 500, 'message': "The package rating system choked on at least one of the metrics."})
                        
                # else:
                #     return convertJSONFormat(400, {'code': 400, 'message': 'No such package.'})
            if packageFound == 0:
                return convertJSONFormat(400, {'code': 400, 'message': 'Package does not have a URL'})
        except Exception:
            return convertJSONFormat(400, {'code': 400, 'message': 'No such package.'})
    except Exception:
        return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
    
"""
/reset URL:
"""
@app.route("/reset", methods=['DELETE'])
def resetRegistry():
    checkValues = []
    checkValues = checkAuth()
    try:
        request.get_data()
        if checkValues:
            if checkValues[0] == 0:
                return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to reset the registry.'})
        else:
                return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
        db = firebase.database()
        #Query for all packages:
        packages = db.child("Packages")
        try:
            packages.remove()
            return convertJSONFormat(200, {'code': 200, 'message': 'Registry is reset.'})
        except Exception:
            return convertJSONFormat(401, {'code': 401, 'message': 'Something went wrong when trying to reset the registry!'})
    except Exception:
        return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})

"""
/packages URLS:
"""
@app.route("/packages", methods=['GET'])
def getPackages():
    try:
        # request.get_data()

        offset = 1
        try:
            offset = request.args.get('offset')
        except Exception:
            pass

        offset *= 10

        # if(checkAuth() == 0): 
        #     return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to view the registry.'})
        checkValues = []
        checkValues = checkAuth()
        request.get_data()
        data = json.loads(request.data.decode('utf-8'))
        if checkValues:
            if checkValues[0] == 0:
                return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to add to the registry.'})
        else:
            return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})

        try:
            db = firebase.database()
            allConditionsSatisfied = 1
            response = []
            #Query for all packages:
            # packages = db.child("Packages").get().val()
            # print(packages)
            for packageKey in db.child("Packages").get().val():
                for comparePackage in data:
                    if 'Name' in comparePackage:
                        # print(comparePackage['Name'])
                        # print(db.child("Packages").child(packageKey).get().val()['Metadata']['Name'])
                        if db.child("Packages").child(packageKey).get().val()['Metadata']['Name'] == comparePackage['Name']:
                            allConditionsSatisfied = 1
                        else:
                            allConditionsSatisfied = 0
                    if 'ID' in comparePackage:
                        # print(comparePackage['ID'])
                        # print(db.child("Packages").child(packageKey).get().val()['Metadata']['ID'])
                        if db.child("Packages").child(packageKey).get().val()['Metadata']['ID'] == comparePackage['ID']:
                            allConditionsSatisfied = 1
                        else:
                            allConditionsSatisfied = 0
                    if 'Version' in comparePackage:
                        # print(comparePackage['Version'])
                        # print(db.child("Packages").child(packageKey).get().val()['Metadata']['Version'])
                        if db.child("Packages").child(packageKey).get().val()['Metadata']['Version'] == comparePackage['Version']:
                            allConditionsSatisfied = 1
                        else:
                            allConditionsSatisfied = 0
                    # print(allConditionsSatisfied)
                    if allConditionsSatisfied == 1:
                        response.append(db.child("Packages").child(packageKey).get().val()['Metadata'])
            return convertJSONFormat(200, response)
        except Exception:
            return convertJSONFormat(400, {'code': 400, 'message': 'Error! Something went wrong when processing your request!'})   
    except Exception:
        return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})

"""
/package URL:
"""
@app.route("/package", methods=['POST'])
def createPackage():
    # print("create package called")
    packageURL = None
    packageContent = None
    checkValues = []
    checkValues = checkAuth()
    request.get_data()
    if checkValues:
        if checkValues[0] == 0:
            return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to add to the registry.'})
    else:
            return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})


    currentUserName = checkValues[1]
    currentIsAdmin = checkValues[2]
    #Load Request Body as JSON:
    req_body = json.loads(request.data.decode('utf-8'))
    # print(req_body)
    

    #Parse Data as metadata and data:
    try:
        metadata = req_body['metadata']
        data = req_body['data']

        if 'URL' in data:
            packageURL = data['URL']
            # print(packageURL)
        elif 'Content' in data:
            packageContent = data['Content']
        
        # print(packageURL)
        # print(packageContent)

    except Exception:
        return convertJSONFormat(400, {'code': 400, 'message': 'Malformed request.'})
    
    db = firebase.database()

    try:
        
        #Check if package exists:
        if db.child("Packages").get().val():
            for packageKey in db.child("Packages").get().val():
                # print(packageKey)
                if db.child("Packages").child(packageKey).get().val()['Metadata']['Name'] == metadata['Name'] and db.child("Packages").child(packageKey).get().val()['Metadata']['ID'] == metadata['ID'] and db.child("Packages").child(packageKey).get().val()['Metadata']['Version'] == metadata['Version']:
                    return convertJSONFormat(403, {'code': 403, 'message': 'Package exists already.'})
        #Check if Package is INGESTIBLE
        if packageURL:
            # print("URL Rating Startd")
            # print(packageURL)
            packageRatings = rate.call_main(packageURL)
            # print(packageRatings)
            if packageRatings[0] > 0.5:
            # data = {'Name': metadata['Name'], 'Version': metadata['Version'], 'ID': metadata['ID'], 'packageData': data}
            # db.child("Packages").child(metadata['ID']).set(data)
                packageMetaData = {'Name': metadata['Name'], 'Version': metadata['Version'], 'ID': metadata['ID']}
                data = {'Ingest' : {'User':{'name': currentUserName, 'isAdmin': currentIsAdmin},'Date': f"{datetime.datetime.now()}",'PackageMetadata': packageMetaData, 'Action': "Create" }, 'Metadata': packageMetaData, 'packageData': data}
                db.child("Packages").child(metadata['ID']).set(data)
            else:
                return convertJSONFormat(400, {'code': 400, 'message': 'Package trying to get ingested has a rating lower than 0.5'})
            # print("Pakage Created when URL was provided")
        if packageContent:
            # print("The world is here")
            # print("reched here")
            # base64_message = base64.b64decode(data)
    
            # print(type(base64_message))
            # contentOutput = base64_message.decode()
            # print(contentOutput)
            # print("reched here 2")
            # output = json.loads(output)
            # print("reched here 3")
           
            packageMetaData = {'Name': metadata['Name'], 'Version': metadata['Version'], 'ID': metadata['ID']}
            data = {'Create' : {'User':{'name': currentUserName, 'isAdmin': currentIsAdmin},'Date': f"{datetime.datetime.now()}",'PackageMetadata': packageMetaData,'Action': "Create"}, 'Metadata': packageMetaData, 'packageData': data}
            db.child("Packages").child(metadata['ID']).set(data)

        # print("metadata set")
        # db.set(data)
        
        return convertJSONFormat(201, packageMetaData)
    except Exception:
        return convertJSONFormat(400, {'code': 400, 'message': 'Something went wrong when trying to add a package.'})
# def createPackage():
#     try:
#         request.get_data()
        
#         if(checkAuth() == 0): 
#             return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to add to the registry.'})
        
#         #Load Request Body as JSON:
#         req_body = json.loads(request.data.decode('utf-8'))

#         #Parse Data as metadata and data:
#         try:
#             metadata = req_body['metadata']
#             data = req_body['data']
#         except Exception:
#             return convertJSONFormat(400, {'code': 400, 'message': 'Malformed request.'})
        
#         db = firebase.database()
#         try:
#             #Check if package exists:
#             if list(db.child("package").order_by_child("ID").equal_to(metadata["id"].get())):
#                 return convertJSONFormat(403, {'code': 403, 'message': 'Package exists already.'})

#             data = {'Name': metadata['Name'], 'Version': metadata['Version'], 'ID': metadata['ID']}
#             db.set(data)
            
#             return convertJSONFormat(201, data)
#         except Exception:
#             return convertJSONFormat(400, {'code': 400, 'message': 'Something went wrong when trying to add a package.'})
#     except Exception:
#         return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})

"""
/package/byName/<name> URLS:
"""
@app.route("/package/byName/<name>", methods=['GET'])
def getPackageByName(name):
    try:
        checkValues = []
        returnData = []
        checkValues = checkAuth()
        request.get_data()
        if checkValues:
            if checkValues[0] == 0:
                return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to modify the package.'})
        else:
            return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
        # request.get_data()
        
        # if(checkAuth() == 0): 
        #     return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to view the package.'})

        db = firebase.database()
        packageNotFound = 1

        try:
            #Query for all packages:
            # packages = db.child("package").order_by_child("Name").equal_to(name).get()
            for packageKey in db.child("Packages").get().val():
                # print(packageKey)
                # print(name)
                # print(db.child("Packages").child(packageKey).get().val())
                # for actions in db.child("Packages").child(packageKey).get().val():
                    # print(actions)
                if db.child("Packages").child(packageKey).get().val()['Metadata']['Name'] == name:
                    newData = {'Download' : {'User':{'name': checkValues[1], 'isAdmin': checkValues[2]},'Date': f"{datetime.datetime.now()}",'PackageMetadata': db.child("Packages").child(packageKey).get().val()['Metadata'],'Action': "Download"}}
                    db.child("Packages").child(packageKey).update(newData)
                    # print("Reached here")
                    packageNotFound = 0
                    for actions in db.child("Packages").child(packageKey).get().val():
                        # print(actions)
                        if actions != 'Metadata' and actions != 'packageData':
                            # print(actions)
                            # data = {'PackageMetadata': db.child("Packages").child(packageKey).child(actions).get().val()['PackageMetadata'], 'Date': db.child("Packages").child(packageKey).child(actions).get().val()['Date'],'Action': db.child("Packages").child(packageKey).child(actions).get().val()['Action'], 'User': db.child("Packages").child(packageKey).child(actions).get().val()['User']}
                            data = db.child("Packages").child(packageKey).child(actions).get().val()
                            returnData.append(data)
                    return convertJSONFormat(200, returnData)
            if packageNotFound:
                return convertJSONFormat(400, {'code': 400, 'message': 'No such package.'})
        except Exception:
            return convertJSONFormat(400, {'code': 400, 'message': 'Error in retrieving package.'})
    except Exception:
        return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
    

@app.route("/package/byName/<name>", methods=['DELETE'])
def deletePackageVersions(name):
    try:
        checkValues = []
        checkValues = checkAuth()
        request.get_data()
        if checkValues:
            if checkValues[0] == 0:
                return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to modify the package.'})
        else:
            return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
        
        # if(checkAuth() == 0): 
        #     return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission '})

        db = firebase.database()
        packageNotFound = 1

        #Try Deleting the package:
        try:
            for packageKey in db.child("Packages").get().val():
                # print(packageKey)
                # print(db.child("Packages").get().val()[packageKey])
                if db.child("Packages").child(packageKey).get().val()['Metadata']['Name'] == name:
                    # print("Package Removed")
                    packageNotFound = 0
                    db.child("Packages").child(packageKey).remove()
                    return convertJSONFormat(200, {'code': 200, 'message': 'Package is deleted.'})
            if packageNotFound:
                return convertJSONFormat(400, {'code': 400, 'message': 'No such package.'})
        except Exception:
            return convertJSONFormat(400, {'code': 400, 'message': 'Error in retrieving package for deletion.'})

        # if(list(packages.get())==[]):
        #     return convertJSONFormat(400, {'code': 400, 'message': 'No such package.'})
        # try:
        #     packages.remove()
        #     return convertJSONFormat(200, {'code': 200, 'message': 'Package is deleted.'})
        # except Exception:
        #     return convertJSONFormat(400, {'code': 400, 'message': 'Error in deleting package.'})
    except Exception:
        return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})
#     try:
#         request.get_data()
        
#         if(checkAuth() == 0): 
#             return convertJSONFormat(401, {'code': 401, 'message': 'You do not have permission to modify the package.'})

#         db = firebase.database()

#         #Query for all packages:
#         try:
#             packages = db.child("package").order_by_child("Name").equal_to(name)
#         except Exception:
#             return convertJSONFormat(400, {'code': 400, 'message': 'Error in retrieving package for deletion.'})

#         if(list(packages.get())==[]):
#             return convertJSONFormat(400, {'code': 400, 'message': 'No such package.'})

#         try:
#             packages.remove()
#             return convertJSONFormat(200, {'code': 200, 'message': 'Package is deleted.'})
#         except Exception:
#             return convertJSONFormat(400, {'code': 400, 'message': 'Error in deleting package.'})
#     except Exception:
#         return convertJSONFormat(400, {'code': 400, 'message': 'Unknown Error!  Please ensure that your request was made properly!'})

class Authenticate(Resource):
    # @marshal_with(metadata_payload)
    def put(self):
        try:
            data = request.get_data()
            # print(data)
            data = json.loads(data)
            # print(data['User']['name'])
            user_info_dict = data['User']
            user_name = user_info_dict['name']
            is_admin = user_info_dict['isAdmin']
            user_password = data['Secret']['password']
            app.config['SECRET_KEY'] = user_password
        
            token = jwt.encode({'user' : user_name, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=600)}, app.config['SECRET_KEY'])
            # print(token.decode("utf-8"))
            # token = json.loads(token)
            token = token.decode("utf-8")

            # user = auth.sign_in_with_email_and_password(userName, userPassword)
            # token_with_additional_claims = auth.create_custom_token(token, {"isAdmin": isAdmin})

            # Get a reference to the database service
            db = firebase.database()

            # data to save
            data = {"User": {"name": user_name,"isAdmin": is_admin},"Secret": {"password": user_password},"Token": token}
            # token_with_additional_claims = auth.create_custom_token(token, {"isAdmin": isAdmin})

            # Pass the user's idToken to the push method
            db.child("Users").child(user_name).set(data)



            # response = app.response_class(
            #     response=token,
            #     status=201,
            #     mimetype='application/json'
            #     )
            return token
        except:
            return None, 400

api.add_resource(Authenticate, "/authenticate")


if __name__ == '__main__':
	# Start the server on "127.0.0.1:8001"
    app.run(port=8001, host='127.0.0.1', debug=True, use_evalex=False)
