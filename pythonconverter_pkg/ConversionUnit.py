
#custom modules
import importlib.util
from pythonconverter_pkg import DatabaseInterfaceFactory as dbFactory
import json

class ConversionUnit:
	def __init__(self):
		print("init Converison Unit")
		self.__inputFile=""
		self.__outputFile=""
		self.__conType=""
		self.__conFile=""
		self.__userScriptPath=""
		self.__userScript=""
		self.__session=""
		self.__eparameter=dict()
		self.__iMap=dict()
		self.__oMap=dict()
		self.__dbFact = dbFactory.DatabaseInterfaceFactory()
		self.__iInt = self.__dbFact.InputInterface(self.__conType)
		self.__oInt = self.__dbFact.OutputInterface(self.__conType)

	def setInputFile(self, inputFile):
		self.__inputFile=inputFile

	def setOutputFile(self, outputFile):
		self.__outputFile=outputFile

	def setType(self, conType):
		self.__conType = conType

	def setConFile(self, conFile):
		self.__conFile = conFile

	
	def setUserScript(self,file):
		retVal=True
		self.__userScriptPath=file
		try:
			if file.find('/') != -1:
				spec = importlib.util.spec_from_file_location("UserScript", self.__userScriptPath)
				self.__userScript = importlib.util.module_from_spec(spec)
				spec.loader.exec_module(self.__userScript)
			else:
				self.__userScript=importlib.import_module(self.__userScriptPath)
		except:
			retVal=False
		return retVal
		
		



	def ShowRecords(self):
		self.__iInt = self.__dbFact.InputInterface(self.__conType)
		self.__iInt.openDatabase(self.__inputFile)
		ret = self.__iInt.readRecordList()
		return ret

	def convert(self,p_record):
		self.__record = p_record
		self.__iInt.openDatabase(self.__inputFile)
		self.__oInt.openDatabase(self.__outputFile)
		self.__read()
		#print(self.__iMap)
		self.__manipulateSet()
		print(self.__oMap)
		self.__write()
		self.__iInt.closeDatabase()

	def __readTransactionList(self):
		return self.__iInt.readDatasetList(self.__record)

	def __readStaticData(self):
		return self.__iInt.readStaticData(self.__record)

	#read from input database
	def __read(self):
		print("not implemented yet")
		transList = self.__readTransactionList()
		self.__iMap[self.__record]=dict()
		self.__iMap[self.__record]["dynamic"]=dict()
		self.__iMap[self.__record]["static"]=dict()
		for con in transList :
			tmpDict=dict()
			tmpDict["contentset_names"]=con["contentset_names"]
			tmpDict["timestemp"]=con["start_time"]
			tmpDict["guiContext"]=con["guicontext_name"]
			tmpDict["values"]=self.__iInt.readDataset(con["transaction_name"])
			self.__iMap[self.__record]["dynamic"][con["transaction_name"]]=tmpDict
		self.__iMap[self.__record]["static"]=self.__readStaticData()
		
			

	
	# manipulate input dataset (dict)
	def __manipulateSet(self):
		if self.__userScriptPath != "" :
			manUnit=self.__userScript.UserScript()
			manUnit.setInput(self.__iMap)
			manUnit.manipulate()
			self.__oMap = manUnit.getOutput()


	# write data to output database
	def __write(self):
		self.__oInt.writeDataset(self.__oMap)
		self.__oInt.saveChanges()




