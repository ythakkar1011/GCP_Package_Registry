import handler
import unittest
from metrics import Metrics


class TestHandler(unittest.TestCase):
    def test_rampUpScore_high(self):
        metricObj = Metrics("https://github.com/jquery/jquery")
        metricObj.setRampUp()
        self.assertGreaterEqual(metricObj.rampUpScore, 0.5)

    def test_rampUpScore_equalToOne(self):
        metricObj = Metrics("https://github.com/browserify/browserify")
        metricObj.setRampUp()
        self.assertEqual(metricObj.rampUpScore, 1.0)

    def test_dependencyScore_high(self):
        metricObj = Metrics("https://github.com/expressjs/express")
        metricObj.setDependencyScore()
        self.assertGreater(metricObj.dependencyScore,0.8)

    def test_dependencyScore_low(self):
        metricObj = Metrics("https://github.com/cloudinary/cloudinary_npm")
        metricObj.setDependencyScore()
        self.assertLess(metricObj.dependencyScore,0.5)
    
    def test_rampUpScore_low(self):
        metricObj = Metrics("https://github.com/kkemple/memoize-async")
        metricObj.setRampUp()
        self.assertLess(metricObj.rampUpScore, 0.5)

    def test_responsiveMaintainers_low(self):
        metricObj = Metrics("https://github.com/jonschlinkert/kind-of")
        metricObj.setResponsiveMaintainer()
        self.assertLess(metricObj.responsiveMaintainerScore,0.5)

    def test_responsiveMaintainers_high(self):
        metricObj = Metrics("https://github.com/facebook/react")
        metricObj.setResponsiveMaintainer()
        self.assertGreater(metricObj.responsiveMaintainerScore,0.8)

    def test_responsiveMaintainers_moderate(self):
        metricObj = Metrics("https://www.github.com/aws/aws-sdk-js")
        metricObj.setResponsiveMaintainer()
        self.assertEqual(metricObj.responsiveMaintainerScore,0.5)

    def test_correctness_high(self):
        metricObj = Metrics("https://www.github.com/facebook/react")
        metricObj.setCorrectness()
        self.assertGreaterEqual(metricObj.correctnessScore,0.5)

    def test_correctness_low(self):
        metricObj = Metrics("https://github.com/jonschlinkert/kind-of")
        metricObj.setCorrectness()
        self.assertLess(metricObj.correctnessScore,0.5)

    def test_license_1_other(self):
        metricObj = Metrics("https://github.com/lodash/lodash")
        metricObj.setLicense()
        self.assertEqual(metricObj.licenseScore,1)

    def test_license_1_valid(self):
        metricObj = Metrics("https://github.com/expressjs/express")
        metricObj.setLicense()
        self.assertEqual(metricObj.licenseScore,1)

    def test_license_invalid(self):
        metricObj = Metrics("https://github.com/j234ohnathansmile/dummyrepo")
        metricObj.setLicense()
        self.assertEqual(metricObj.licenseScore, 0)

    def test_netScore_low(self):
        metricObj = Metrics("https://github.com/deepmind/alphafold")
        metricObj.runMetrics()
        self.assertEqual(metricObj.netScore,0)

    def test_netScore_high(self):
        metricObj = Metrics("https://github.com/VirusTotal/yara")
        metricObj.runMetrics()
        self.assertEqual(metricObj.netScore,0.8)	

    def test_getRepoInfo_invalid(self):
        response = handler.getRepoInfo("john", "dummyRepo")
        self.assertEqual(response['message'],"Not Found")

    def test_getCommunityProfile_invalid(self):
        response = handler.getCommunityProfile("john", "dummyRepo")
        self.assertEqual(response['message'],'Not Found')

    def test_getCommits_invalid(self):
        response = handler.getCommunityProfile("john", "dummyRepo")
        self.assertEqual(response['message'],'Not Found')

    def test_getIssues_invalid(self):
        response = handler.getIssues("john", "dummyRepo")
        self.assertEqual(response['message'],'Not Found')  

    def test_getRepoInfo_valid(self):
        response = handler.getRepoInfo("nullivex", "nodist")
        self.assertNotEqual(len(response),0)

    def test_getCommunityProfile_valid(self):
        response = handler.getCommunityProfile("nullivex", "nodist")
        self.assertGreater(len(response),2)

    def test_getCommits_valid(self):
        response = handler.getCommits("cloudinary", "cloudinary_npm") 
        self.assertGreater(len(response),0)

    def test_getRepoInfo_valid(self):
        response = handler.getRepoInfo("nullivex", "nodist")
        self.assertNotEqual(len(response),0)

    def test_getIssues_valid(self):
        response = handler.getIssues("nullivex", "nodist")
        self.assertNotEqual(len(response),0)

    def test_getGithubUrl_valid(self):
        response = handler.getGithubUrl("express")
        self.assertNotEqual(len(response),0)

if __name__ == '__main__':
    unittest.main()
