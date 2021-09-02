import unittest
from pythonconverter_pkg import CppInterface

class TestCppInterface(unittest.TestCase):

    def test_mtDatabaseConversionGuiOnly(self):
        CppInterface.setInputPath("test/mttest.db")
        CppInterface.setOutputPath("test/result.xml")
        CppInterface.setSession("guionly")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)
        CppInterface.setOutputPath("test/main.xml")
        CppInterface.setEngine("zeraconverterengines.MTVisMain")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)

    def test_mtDatabaseConversionCustom(self):
        CppInterface.setInputPath("test/mttest.db")
        CppInterface.setOutputPath("test/result.xml")
        CppInterface.setSession("custom")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)
        CppInterface.setOutputPath("test/main.xml")
        CppInterface.setEngine("zeraconverterengines.MTVisMain")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)

    def test_mtDatabaseConversionAll(self):
        CppInterface.setInputPath("test/mttest.db")
        CppInterface.setOutputPath("test/result.xml")
        CppInterface.setSession("all")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)
        CppInterface.setOutputPath("test/main.xml")
        CppInterface.setEngine("zeraconverterengines.MTVisMain")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)

if __name__ == '__main__':
    unittest.main()