import unittest
from pythonconverter_pkg import CppInterface

class TestCppInterface(unittest.TestCase):

    def test_databaseConversion(self):
        CppInterface.setInputPath("test/test.db")
        CppInterface.setOutputPath("test/out.xml")
        CppInterface.setSession("ses1all")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),True)
        

if __name__ == '__main__':
    unittest.main()