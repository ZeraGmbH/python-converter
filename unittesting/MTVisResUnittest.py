import unittest
from pythonconverter_pkg import CppInterface
from xml.dom import minidom

class MTVisResUnittest(unittest.TestCase):
    def setUp(self) :
        CppInterface.setInputPath("test/mttest.db")
        CppInterface.setOutputPath("test/result.xml")
        CppInterface.setSession("guionly")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)
        self.resultXml = minidom.parse("test/result.xml")
    
    def getTotalElements(self, tagName):
        return self.resultXml.getElementsByTagName(tagName).length

    def getValueOfFirstChild(self, tagName, eleNum):
        return self.resultXml.getElementsByTagName(tagName)[eleNum].firstChild.nodeValue
        
    def test_sessionDeviceInfo(self):
        for i in range(self.getTotalElements('ID')) : 
            self.assertEqual(self.getValueOfFirstChild('ID', i), "guionly")

        for i in range(self.getTotalElements('Language')) : 
            self.assertEqual(self.getValueOfFirstChild('Language', i), "DEU")
    
        for i in range(self.getTotalElements('Device-Typ')) : 
            self.assertEqual(self.getValueOfFirstChild('Device-Typ', i), "mt310s2")
        
        for i in range(self.getTotalElements('Device-No')) : 
            self.assertEqual(self.getValueOfFirstChild('Device-No', i), "50059479")

if __name__ == '__main__':
    unittest.main()