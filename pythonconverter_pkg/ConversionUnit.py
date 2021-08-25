
#custom modules
import importlib.util
from pythonconverter_pkg import DatabaseInterfaceFactory as dbFactory
import json
import warnings
import logging

class ConversionUnit:
    def __init__(self):
        print("init Converison Unit")
        self.__inputFile = ""
        self.__outputFile = ""
        self.__conType = ""
        self.__conFile = ""
        self.__userScriptPath = ""
        self.__userScript = ""
        self.__session = ""
        self.__filter = ""
        self.__eparameter = dict()
        self.__iMap = dict()
        self.__oMap = dict()
        self.__userScriptErrors = 0
        self.__errorRegister = 0
        self.__dbFact = dbFactory.DatabaseInterfaceFactory()
        self.__iInt = self.__dbFact.InputInterface(self.__conType)
        self.__oInt = self.__dbFact.OutputInterface(self.__conType)

    def getErrorRegister(self):
        return self.__errorRegister

    def clearErrorRegister(self):
        self.__errorRegister = 0

    def getUserScriptErrors(self):
        return self.__userScriptErrors

    def clearUserScriptErrors(self):
        self.__userScriptErrors = 0

    def setInputFile(self, inputFile):
        self.__inputFile=inputFile
        return True

    def setOutputFile(self, outputFile):
        self.__outputFile=outputFile
        return True

    def setType(self, conType):
        self.__conType = conType
        return True

    def setFilter(self, filter):
        self.__filter = filter
        return True

    def setConFile(self, conFile):
        self.__conFile = conFile
        return True

    def seteParam(self, eparams):
        retVal=True
        self.__eparameter = dict()
        if eparams:
            try:
                json_acceptable_string = eparams.replace("'", "\"")
                self.__eparameter = json.loads(json_acceptable_string)
            except:
                self.__eparameter = dict()
                self.__errorRegister = self.__errorRegister | (1  << 9)
                logging.warning("Bad Parameters. Ignoring!")
        return retVal

    def setUserScript(self, file):
        retVal = True
        self.__userScriptPath = file
        try:
            if file.find('/') != -1:
                spec = importlib.util.spec_from_file_location("UserScript", self.__userScriptPath)
                self.__userScript = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.__userScript)
            else:
                self.__userScript = importlib.import_module(self.__userScriptPath)
        except:
            self.__errorRegister = self.__errorRegister | (1  << 0)
            retVal = False
        return retVal

    def ShowSessions(self):
        self.__iInt = self.__dbFact.InputInterface(self.__conType)
        self.__iInt.openDatabase(self.__inputFile)
        ret = self.__iInt.readSessionList()
        return ret

    def convert(self, p_session):
        retVal = True
        try:
            self.__session = p_session
            if not self.__iInt.openDatabase(self.__inputFile):
                self.__errorRegister = self.__errorRegister | (1  << 1)
                raise Exception("Fatal Error")
            if not self.__oInt.openDatabase(self.__outputFile):
                self.__errorRegister = self.__errorRegister | (1  << 2)
                raise Exception("Fatal Error")
            if not self.__read():
                self.__errorRegister = self.__errorRegister | (1  << 3)
                raise Exception("Fatal Error")
            if not self.__manipulateSet():
                self.__errorRegister = self.__errorRegister | (1  << 4)
                raise Exception("Fatal Error")
            if not self.__write():
                self.__errorRegister = self.__errorRegister | (1  << 5)
                raise Exception("Fatal Error")
            if not self.__iInt.closeDatabase():
                self.__errorRegister = self.__errorRegister | (1  << 8)
        except Exception as error:
            retVal = False
        return retVal

    def __readTransactionList(self):
        return self.__iInt.readDatasetList(self.__session)

    def __readStaticData(self):
        return self.__iInt.readStaticData(self.__session)

    # read from input database
    def __read(self):
        retVal = True
        try:
            transList = self.__readTransactionList()
            if len(transList) is 0:
                self.__errorRegister = self.__errorRegister | (1  << 10)
            self.__iMap[self.__session] = dict()
            self.__iMap[self.__session]["dynamic"] = dict()
            self.__iMap[self.__session]["static"] = dict()
            for con in transList:
                # only write to dict, if transaction fits filter or no filter is set.
                if con["transaction_name"].find(self.__filter) != -1 or not self.__filter:
                    tmpDict = dict()
                    tmpDict["contentset_names"] = con["contentset_names"]
                    tmpDict["timestemp"] = con["start_time"]
                    tmpDict["guiContext"] = con["guicontext_name"]
                    tmpDict["values"] = self.__iInt.readDataset(
                        con["transaction_name"])
                    self.__iMap[self.__session]["dynamic"][con["transaction_name"]] = tmpDict
            self.__iMap[self.__session]["static"] = self.__readStaticData()
        except:
            retVal = False
        return retVal

    # manipulate input dataset (dict)

    def __manipulateSet(self):
        retVal = True
        if self.__userScriptPath != "":
            try:
                manUnit = self.__userScript.UserScript()
                manUnit.setParams(self.__eparameter)
                manUnit.setInput(self.__iMap)
                self.__userScriptErrors = manUnit.manipulate()
                self.__oMap = manUnit.getOutput()
            except:
                retVal = False
        else:
            retVal = False
        return retVal

    # write data to output database

    def __write(self):
        retVal=True
        try:
            self.__oInt.writeDataset(self.__oMap)
            self.__oInt.saveChanges()
        except:
            retVal=False
        return retVal
