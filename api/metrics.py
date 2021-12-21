import datetime as dt
import requests
from git import Repo
import os
import shutil
import re
import handler
import logging
from backports.datetime_fromisoformat import MonkeyPatch


class Metrics:
    def __init__(self, url: str):
        self.repoUrl = url
        self.moduleOwner = url.split('/')[-2]
        self.moduleName = url.split('/')[-1]
        self.netScore = -1
        self.rampUpScore = -1
        self.correctnessScore = -1
        self.busFactorScore = -1
        self.responsiveMaintainerScore = -1
        self.licenseScore = -1
        self.dependencyScore = -1

    def __repr__(self):
        reprString =  f"""
        Repo URL: {self.repoUrl} \n \
        Repo Owner: {self.moduleOwner} \n \
        Repo Module Name: {self.moduleName} \n \
        Repo Net Score: {self.netScore} \n \
        Repo Ramp Up Score: {self.rampUpScore} \n \
        Repo Correctness Score: {self.correctnessScore} \n \
        Repo Bus Factor Score: {self.busFactorScore} \n \
        Repo Responsive Maintainer Score: {self.responsiveMaintainerScore} \n \
        Repo License Score: {self.licenseScore} \n \
        Repo Dependency Score: {self.dependencyScore} \n \
        """

        return reprString

    def setNet(self) -> None:
        if self.licenseScore == 0:
            self.netScore = 0
            return

        weights = {
            "rampUpScore": 0.25,
            "correctnessScore": 0.2,
            "busFactorScore": 0.35,
            "responsiveMaintainerScore": 0.2,
            "dependecyScore": 0.1
        }

        self.netScore = self.rampUpScore * weights["rampUpScore"] \
            + self.correctnessScore * weights["correctnessScore"] \
            + self.busFactorScore * weights["busFactorScore"] \
            + self.responsiveMaintainerScore * weights['responsiveMaintainerScore'] \
            + self.dependencyScore * weights['dependecyScore']

        self.netScore = round(self.netScore, 2)

    def setRampUp(self) -> None:

        rampUpScore = 0

        response = handler.getRepoInfo(self.moduleOwner, self.moduleName)
        # logging.debug(f"RampUp(repoInfo) response for {self.moduleName} is empty: {len(response) == 0}")
        commProfile = handler.getCommunityProfile(self.moduleOwner, self.moduleName)
        # logging.debug(f"RampUp(commProfile) response for {self.moduleName} is empty: {len(commProfile) == 0}")

        try:
            if 'documentation' in commProfile:
                if commProfile['documentation'] is not None:
                    rampUpScore += 0.4
            if 'has_wiki' in response:
                if response['has_wiki']:
                    rampUpScore += 0.3
            if 'has_pages' in response:
                if response['has_pages']:
                    rampUpScore += 0.2
        except TypeError:
            # logging.info("(setRampUp) API response doesn't have the necessary fields for metric calculation!")
            pass

        #Clone Repo
        # Repo.clone_from(self.repoUrl, './repositories/' + self.moduleName)
        # logging.info(f"The repo for {self.moduleName} is cloned to your local machine!")

        # for filename in os.listdir('./repositories/' + self.moduleName):
        #     if filename.lower().startswith('readme'):
        #         f = open('./repositories/' + self.moduleName + '/' + filename, 'r')
        #         break
        # else:
        #     shutil.rmtree('./repositories/' + self.moduleName)
        #     os.rmdir('./repositories')
        #     self.rampUpScore = round(rampUpScore, 2)
        #     return

        # readme = f.readlines()

        # increments = {"installation": 0.2, "install": 0.2,"usage": 0.2, "wiki": 0.1, "description": 0.1, "resources": 0.1, "faq": 0.1,"setup":0.2,"troubleshooting":0.1,"frequently asked questions":0.1,"additional resources":0.1,"overview":0.1,"methods":0.2,"getting started":0.2,"commands":0.1,"features":0.2,"modules":0.1}

        # for line in readme:
        #     if line.startswith("#"):
        #         match = re.search(r"installation|install|wiki|setup|usage|methods|modules|description|overview|resources|faq|frequently asked questions|additional resources|troubleshooting|getting started|commands|features",line,flags=re.I)
        #         if match:
        #             match = match.group().lstrip('# ').lower()
        #             rampUpScore += increments[match]
        # f.close()
        # #Delete cloned repo
        # shutil.rmtree('./repositories/' + self.moduleName)
        # os.rmdir('./repositories')
        # logging.info(f"The repo for {self.moduleName} is deleted from your local machine!")

        if rampUpScore >= 1.0:
            rampUpScore = 1.0
        self.rampUpScore = round(rampUpScore, 2)

    def setCorrectness(self) -> None:
        response = handler.getRepoInfo(self.moduleOwner, self.moduleName)
        logging.debug(f"ResponsiveMaintainer response for {self.moduleName} is empty: {len(response) == 0}")
        starVal, forkVal = 0, 0 

        try:
            if 'stargazers_count' in response:
                starCount = response['stargazers_count']
                starVal = min(starCount*0.001, 1)
            if 'forks_count' in response:
                forkCount = response['forks_count']
                forkVal = min(forkCount*0.01, 1) 
        except TypeError:
            logging.info("(setCorrectness) API response doesn't have the necessary fields for metric calculation!")

        self.correctnessScore = round((starVal + forkVal) / 2, 1)

    def setBusFactor(self) -> None:
        response = handler.getCommits(self.moduleOwner, self.moduleName)
        logging.debug(f"BusFactor response for {self.moduleName} is empty: {len(response) == 0}")

        uniqueContributors = set()
        try:
            if len(response) != 0:
                for commit in response:
                    uniqueContributors.add(commit['commit']['author']['name'])
        except TypeError:
            logging.info("(setBusFactor) API response doesn't have the necessary fields for metric calculation!")

        self.busFactorScore = float(round(min(len(uniqueContributors) * 0.2, 1), 1))

    def setResponsiveMaintainer(self) -> None:
        responsivenessScore = 0
        issuesResponse = handler.getIssues(self.moduleOwner, self.moduleName)
        logging.debug(f"ResponsiveMaintainer(issues) response for {self.moduleName} is empty: {len(issuesResponse) == 0}")

        try:
            if len(issuesResponse) > 0:
                # Get issues:
                noOfIssues = 0
                totalDays = 0
                responsivenessScore = 0

                for issue in issuesResponse:
                    if issue['closed_at']:
                        MonkeyPatch.patch_fromisoformat()
                        created = dt.datetime.fromisoformat(issue['created_at'][:-1])
                        closed = dt.datetime.fromisoformat(issue['closed_at'][:-1])
                        totalDays += (closed - created).days
                        noOfIssues += 1

                    averageTimeToResolveIssue = totalDays // noOfIssues
                    if averageTimeToResolveIssue >= 50:
                        responsivenessScore = 0.2
                    elif 25 <= averageTimeToResolveIssue < 50:
                        responsivenessScore = 0.4
                    elif 12 <= averageTimeToResolveIssue < 25:
                        responsivenessScore = 0.5
                    elif 5 <= averageTimeToResolveIssue < 12:
                        responsivenessScore = 0.6
                    elif 2 <= averageTimeToResolveIssue < 5:
                        responsivenessScore = 0.7
                    elif 1 <= averageTimeToResolveIssue < 2:
                        responsivenessScore = 0.8
                    elif 0 <= averageTimeToResolveIssue < 1:
                        responsivenessScore = 0.9
            else:
                self.responsiveMaintainerScore = 0.0
        except TypeError:
            logging.info("(setResponsiveMaintainer) API response doesn't have the necessary fields for metric calculation!")

        self.responsiveMaintainerScore = round(responsivenessScore, 1)

    def setLicense(self) -> None:
        # NOTE: COMPATIBILITY IS BASED OFF DAVID WHEELER'S FLOSS LICENSE GRAPH
        # https://dwheeler.com/essays/floss-license-slide.html
        compatibleLicenses = ['mit', 'x11', 'bsd-2-clause', 'bsd-3-clause', 'bsd-new', 'lgpl-2.1', 'unlicense', 'bsd', 'lgpl v2.1']
        licenseResponse = handler.getLicense(self.moduleOwner, self.moduleName)

        try:
            # CASE 1: License handler could not find a license nor README.
            if 'message' in licenseResponse:
                self.licenseScore = 0
                return

            if 'license' in licenseResponse:
                # CASE 2: License found via github 'licenses' api and is not 'other'
                if licenseResponse['license']['key'] != 'other':
                    if licenseResponse['license']['key'] in compatibleLicenses:
                        self.licenseScore = 1
                    else:
                        self.licenseScore = 0
                    return
                # CASE 3: License processed as 'other'
                else:
                    licenseResponse['content'] = licenseResponse['content'].lower()
                    for compatLicense in compatibleLicenses:
                        # logic taken from https://stackoverflow.com/questions/4154961/find-substring-in-string-but-only-if-whole-words
                        if re.search(r"\b" + compatLicense + r"\b", licenseResponse['content']):
                            self.licenseScore = 1
                            return
                    self.licenseScore = 0
                    return

            # CASE 4: License not found, check README
            licenseResponse['content'] = licenseResponse['content'].lower()
            for compatLicense in compatibleLicenses:
                if re.search(r"\b" + compatLicense + r"\b", licenseResponse['content']):
                    self.licenseScore = 1
                    return
        except TypeError:
            logging.info("(setLicense) API response doesn't have the necessary fields for metric calculation!")

        self.licenseScore = 0
    
    def setDependencyScore(self) -> None:
        issuesResponse = handler.getDependencies(self.moduleOwner, self.moduleName)
        logging.debug(f"ResponsiveMaintainer(issues) response for {self.moduleName} is empty: {len(issuesResponse) == 0}")
        totalDependencies = len(issuesResponse)
        pinnedDependencies = 0;
        nonPinnedDependencies = 0;
        
        try:
            if  totalDependencies > 0:
                for dependency in issuesResponse:
                    first_dot = issuesResponse[dependency].find(".")
                    second_dot = issuesResponse[dependency].rfind(".")
                    firstChar = len(issuesResponse[dependency])
                    major = issuesResponse[dependency][0:first_dot]
                    minor = issuesResponse[dependency][first_dot + 1:second_dot]
                    patch = issuesResponse[dependency][second_dot + 1:firstChar]

                    if major == '0' and minor == '0' and patch:
                        pinnedDependencies += 1
                    elif bool(re.match("\~[0-9]+", major)) and bool(re.match("[0-9]+", minor)):
                        pinnedDependencies += 1
                    elif bool(re.match("\=[0-9]+", major)) and  bool(re.match("[0-9]+", minor)):
                        pinnedDependencies += 1
                    elif bool(re.match("[0-9]+", major)) and bool(re.match("[0-9]+", minor)):
                        pinnedDependencies += 1
                    elif bool(re.match("\^[0-9]+", major)) and  bool(re.match("[0-9]+", minor)):
                        nonPinnedDependencies += 1
                    elif bool(re.match("\<\=*[0-9]+", major)) and  bool(re.match("[0-9]+", minor)):
                        nonPinnedDependencies += 1
                    elif bool(re.match("\>\=*[0-9]+", major)) and  bool(re.match("[0-9]+", minor)):
                        nonPinnedDependencies += 1
                    

                self.dependencyScore = pinnedDependencies / totalDependencies
            else:
                self.dependencyScore = 1.0
        except TypeError:
            logging.info("(setResponsiveMaintainer) API response doesn't have the necessary fields for metric calculation!")
        

    def runMetrics(self) -> None:
        self.setRampUp()
        # print("RampUp Work")
        self.setCorrectness()
        # print("setCorrectness Work")
        self.setBusFactor()
        # print("setBusFactor Work")
        self.setResponsiveMaintainer()
        # print("setResponsiveMaintainer Work")
        self.setLicense()
        # print("setLicense Work")
        self.setDependencyScore()
        # print("setDependencyScore Work")
        self.setNet()
        # print("setNet Work")
