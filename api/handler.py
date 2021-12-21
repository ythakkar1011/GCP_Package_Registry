import json
import requests
import datetime as dt
import logging
import os
from dotenv import load_dotenv
import base64
load_dotenv()

header = {
    'accept': 'application/vnd.github.v3+json',
    'Authorization': "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"
}


def getRepoInfo(owner: str, module: str) -> dict:
    response = requests.get(url='https://api.github.com/repos/' + owner + '/' + module, headers=header ).json()
    if len(response) == 0:
        logging.info(f"getRepoInfo response for {module} is empty!")
        logging.debug(f"getRepoInfo response for {module} is empty!")
    return response


def getCommunityProfile(owner: str, module: str) -> dict:
    response = requests.get(url='https://api.github.com/repos/' + owner + '/' + module + '/community/profile', headers=header).json()
    if len(response) == 0:
        logging.info(f"getCommunityProfile response for {module} is empty!")
        logging.debug(f"getCommunityProfile response for {module} is empty! Please check your input URl or authentication tokens")
    return response


def getCommits(owner: str, module: str) -> dict:
    monthAgo = dt.datetime.today() - dt.timedelta(days=30)
    param = {
        'since':  monthAgo.isoformat(),
        'per_page': '100'
    }
    response = requests.get(url='https://api.github.com/repos/' + owner + '/' + module + '/commits', headers=header, params=param).json()
    if len(response) == 0:
        logging.info(f"getCommits response for {module} is empty!")
        logging.debug(f"getCommits response for {module} is empty!")
    return response


def getIssues(owner: str, module: str) -> dict:
    param = {
        'state': 'closed',
        'per_page': '100'
    }
    response = requests.get(url='https://api.github.com/repos/' + owner + '/' + module + '/issues', headers=header, params=param).json()
    if len(response) == 0:
        logging.info(f"getIssues response for {module} is empty!")
        logging.debug(f"getIssues response for {module} is empty!")
    return response

def getLicense(owner: str, module: str) -> dict:
    licenseResponse = requests.get(
        url='https://api.github.com/repos/' + owner + '/' + module + '/license',
        headers=header
    ).json()

    if 'license' in licenseResponse:
        # CASE 2: License found via github 'licenses' api and is not 'other'
        if licenseResponse['license']['key'] != 'other':
            return licenseResponse
        # CASE 3: License processed as 'other'
        else:
            licenseResponse['content'] = base64.b64decode(licenseResponse['content']).decode('utf-8')
            return licenseResponse

    # CASE 4: License not found, check README
    readmeResponse = requests.get(
        url='https://api.github.com/repos/' + owner + '/' + module + '/readme',
        headers=header
    ).json()
    # CASE 1: License handler could not find a license nor README.
    if 'message' in readmeResponse:
        return readmeResponse
    readmeResponse['content'] = base64.b64decode(readmeResponse['content']).decode('utf-8')

    return readmeResponse
def getGithubUrl(packageName: str) -> str:
    response = requests.get(f'https://api.npms.io/v2/package/{packageName}').json()
    if len(response) == 2: # error responses have 2 fields (code and message)
        logging.debug(f"NPM-JS API returned empty response for {packageName}!")
        return None
    return response['collected']['metadata']['links']['repository']

def getDependencies(owner: str, module: str) -> dict:
    dependencies={}
    # baseURL = baseURL + "/contents/package.json"
    # response = requests.get(baseURL, headers=headers)
    # data = response.json()
    # print("Before Requests")
    data = requests.get(url='https://api.github.com/repos/' + owner + '/' + module + '/contents/package.json', headers=header).json()
    # print("After Requests")
    if 'content' in data:
        # print("Getting Here")
        base64_message = base64.b64decode(data['content'])
        output = base64_message.decode()
        output = json.loads(output)
        if 'dependencies' in output:
            dependencies = output['dependencies']
        else:
            dependencies={}
        # print(type(output))
    else:
        output = {}

    return dependencies
