import unittest
from pythonconverter_pkg import CppInterface
from xml.dom import minidom

class MTVisResUnittest(unittest.TestCase):
    def setUp(self) :
        CppInterface.setInputPath("test/testburden.db")
        CppInterface.setOutputPath("test/resultburden.xml")
        CppInterface.setSession("demo01")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)
        self.resultXml = minidom.parse("test/resultburden.xml")
    
    def getTotalElements(self, tagName):
        return self.resultXml.getElementsByTagName(tagName).length

    def getValueOfFirstChild(self, tagName, eleNum):
        return self.resultXml.getElementsByTagName(tagName)[eleNum].firstChild.nodeValue
        
    def test_sessionDeviceInfo(self):
        for i in range(self.getTotalElements('ID')) : 
            self.assertEqual(self.getValueOfFirstChild('ID', i), "demo01")

        for i in range(self.getTotalElements('Language')) : 
            self.assertEqual(self.getValueOfFirstChild('Language', i), "DEU")
    
        for i in range(self.getTotalElements('Device-Typ')) : 
            self.assertEqual(self.getValueOfFirstChild('Device-Typ', i), "mt310s2")
        
        for i in range(self.getTotalElements('Device-No')) : 
            self.assertEqual(self.getValueOfFirstChild('Device-No', i), "50059475")

    def test_BurdenValues(self):
        self.assertEqual(self.getTotalElements('Sb1'), 2)
        self.assertEqual(self.getTotalElements('Sb2'), 2)
        self.assertEqual(self.getTotalElements('Sb3'), 2)

        self.assertEqual(self.getTotalElements('cosB1'), 2)
        self.assertEqual(self.getTotalElements('cosB2'), 2)
        self.assertEqual(self.getTotalElements('cosB3'), 2)

        self.assertEqual(self.getTotalElements('Sn1'), 2)
        self.assertEqual(self.getTotalElements('Sn2'), 2)
        self.assertEqual(self.getTotalElements('Sn3'), 2)

    def test_UPNValues(self):
        self.assertEqual(self.getTotalElements('UPN1'), 2)
        self.assertEqual(self.getTotalElements('UPN2'), 2)
        self.assertEqual(self.getTotalElements('UPN3'), 2)



if __name__ == '__main__':
    unittest.main()