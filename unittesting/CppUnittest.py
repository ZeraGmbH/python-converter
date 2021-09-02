import unittest
from pythonconverter_pkg import CppInterface

class TestCppInterface(unittest.TestCase):
# MT Tests
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
# Com Tests
    #Meas Session
    def test_comMeasDatabaseConversionGuiOnly(self):
        CppInterface.setInputPath("test/comtest_meas.db")
        CppInterface.setOutputPath("test/result.xml")
        CppInterface.setSession("guionly")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)
        CppInterface.setOutputPath("test/main.xml")
        CppInterface.setEngine("zeraconverterengines.MTVisMain")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)

    def test_comMeasDatabaseConversionCustom(self):
        CppInterface.setInputPath("test/comtest_meas.db")
        CppInterface.setOutputPath("test/result.xml")
        CppInterface.setSession("custom")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)
        CppInterface.setOutputPath("test/main.xml")
        CppInterface.setEngine("zeraconverterengines.MTVisMain")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)

    # def test_comMeasDatabaseConversionAll(self):
    #     CppInterface.setInputPath("test/comtest_meas.db")
    #     CppInterface.setOutputPath("test/result.xml")
    #     CppInterface.setSession("all")
    #     CppInterface.setEngine("zeraconverterengines.MTVisRes")
    #     CppInterface.setFilter("Snapshot")
    #     self.assertEqual(CppInterface.convert(),0)
    #     CppInterface.setOutputPath("test/main.xml")
    #     CppInterface.setEngine("zeraconverterengines.MTVisMain")
    #     CppInterface.setFilter("Snapshot")
    #     self.assertEqual(CppInterface.convert(),0)

    #Ref Session
    def test_comRefDatabaseConversionGuiOnly(self):
        CppInterface.setInputPath("test/comtest_ref.db")
        CppInterface.setOutputPath("test/result.xml")
        CppInterface.setSession("gui")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)
        CppInterface.setOutputPath("test/main.xml")
        CppInterface.setEngine("zeraconverterengines.MTVisMain")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)

    #CED Session
    def test_comCedDatabaseConversionGuiOnly(self):
        CppInterface.setInputPath("test/comtest_ced.db")
        CppInterface.setOutputPath("test/result.xml")
        CppInterface.setSession("gui")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)
        CppInterface.setOutputPath("test/main.xml")
        CppInterface.setEngine("zeraconverterengines.MTVisMain")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)

    def test_comCedDatabaseConversionCustom(self):
        CppInterface.setInputPath("test/comtest_ced.db")
        CppInterface.setOutputPath("test/result.xml")
        CppInterface.setSession("custom")
        CppInterface.setEngine("zeraconverterengines.MTVisRes")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)
        CppInterface.setOutputPath("test/main.xml")
        CppInterface.setEngine("zeraconverterengines.MTVisMain")
        CppInterface.setFilter("Snapshot")
        self.assertEqual(CppInterface.convert(),0)

    def test_comCedDatabaseConversionAll(self):
        CppInterface.setInputPath("test/comtest_ced.db")
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