import sys
import re
import logging
import os
from dotenv import load_dotenv
import metrics
import handler


def handleURL(repoUrl: str) -> tuple:
    # This regex checks a repo URL to make sure it's valid
    urlRegex = r'^(https:\/\/github\.com\/.+\/[\w.-]+|https:\/\/www\.npmjs\.com\/package\/[\w.-]+)$'

    # If the url isn't valid, return a tuple of the url and a value of false to indicate invalid.
    # If it is valid, simply log it and continue.
    if re.match(urlRegex, repoUrl):
        logging.debug(f"'{repoUrl}' follows URL regex.")
    else:
        logging.debug(f"'{repoUrl}' does not follow URL regex.")
        return (repoUrl, False)

    # If the url is an npm url, use the npms api to grab the github repo of the npm package
    if 'npmjs' in repoUrl:
        # Grab the package name from the npm link, last word after last slash.
        packageName = re.search(r'\/([\w.-]+)$', repoUrl).group(1)
        githubUrl = handler.getGithubUrl(packageName)
        if githubUrl is None:
            logging.debug(f"Can't find the GithubUrl for {repoUrl}")
            return (githubUrl, False)
        logging.info(f"npmjs link: {repoUrl}, github repo: {githubUrl}.")
        return (githubUrl, True)
    else:
        return (repoUrl, True)


def main() -> None:
    # Check to make sure there is only 1 cli arg (use "2" since the filename of the python file is an arg itself).
    if len(sys.argv) != 2:
        logging.error("There should only be one command line argument: the path to the URL File!")
        sys.exit()

    urlFilePath = sys.argv[1]

    # Check file path to make sure it exists before continuing.
    # If it does not exist, log it and raise an error.
    try:
        urlFile = open(urlFilePath, "r")
    except FileNotFoundError:
        logging.error(f"URL File path invalid! Please check your input. Path given: '{urlFilePath}'")
        raise FileNotFoundError("URL File path is invalid. Please check your input.")

    repoMetricsDict = {}
    repoList = []

    for repoUrl in urlFile.readlines():
        # Remove trailing newline and replace in repoList.
        repoUrl = repoUrl.strip('\n')

        # Handle the URL, check formatting and get github repo if it's an npmjs link.
        githubRepo, isValid = handleURL(repoUrl)

        # If the repo is valid, run the metrics to get scores.
        # If the repo is not valid, make a metrics object but dont get scores. Default is -1 for all scores.
        if isValid:
            repoMetrics = metrics.Metrics(githubRepo)
            repoMetrics.runMetrics()
        else:
            repoMetrics = metrics.Metrics(repoUrl)

        logging.info(repoMetrics)
        repoList.append((repoUrl, repoMetrics.netScore))
        repoMetricsDict[repoUrl] = repoMetrics

    print('URL NET_SCORE RAMP_UP_SCORE CORRECTNESS_SCORE BUS_FACTOR_SCORE RESPONSIVE_MAINTAINER_SCORE LICENSE_SCORE')
    for repoUrl, _ in reversed(sorted(repoList, key=lambda x: x[1])):
        repoMetrics = repoMetricsDict[repoUrl]
        print(f"{repoUrl} {repoMetrics.netScore} {repoMetrics.rampUpScore} {repoMetrics.correctnessScore} {repoMetrics.busFactorScore} {repoMetrics.responsiveMaintainerScore} {repoMetrics.licenseScore}")


def call_main(url):
    load_dotenv()
    # LOG_LEVEL = {'0': logging.CRITICAL, '1': logging.INFO, '2': logging.DEBUG}
    # logging.basicConfig(filename=os.getenv('LOG_FILE'), level=LOG_LEVEL[os.getenv('LOG_LEVEL')])
    #main()
    repoMetricsDict = {}
    repoList = []
    
    url = url.strip('\n')

    # Handle the URL, check formatting and get github repo if it's an npmjs link.
    githubRepo, isValid = handleURL(url)
    print("handleURL(url) works")

        # If the repo is valid, run the metrics to get scores.
        # If the repo is not valid, make a metrics object but dont get scores. Default is -1 for all scores.
    if isValid:
        repoMetrics = metrics.Metrics(githubRepo)
        repoMetrics.runMetrics()
        print(" runMetrics() works")
    else:
        repoMetrics = metrics.Metrics(url)

    # logging.info(repoMetrics)
    repoList.append((url, repoMetrics.netScore))
    repoMetricsDict[url] = repoMetrics

    # print('URL NET_SCORE RAMP_UP_SCORE CORRECTNESS_SCORE BUS_FACTOR_SCORE RESPONSIVE_MAINTAINER_SCORE LICENSE_SCORE')
    for repoUrl, _ in reversed(sorted(repoList, key=lambda x: x[1])):
        repoMetrics = repoMetricsDict[repoUrl]
        # print(f"{repoUrl} {repoMetrics.netScore} {repoMetrics.rampUpScore} {repoMetrics.correctnessScore} {repoMetrics.busFactorScore} {repoMetrics.responsiveMaintainerScore} {repoMetrics.licenseScore}")
        return repoMetrics.netScore, repoMetrics.rampUpScore, repoMetrics.correctnessScore, repoMetrics.busFactorScore, repoMetrics.responsiveMaintainerScore, repoMetrics.licenseScore, repoMetrics.dependencyScore

    

# if __name__ == "__main__":
#     load_dotenv()
#     LOG_LEVEL = {'0': logging.CRITICAL, '1': logging.INFO, '2': logging.DEBUG}
#     logging.basicConfig(filename=os.getenv('LOG_FILE'), level=LOG_LEVEL[os.getenv('LOG_LEVEL')])
#     main()
