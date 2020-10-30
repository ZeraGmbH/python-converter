

class DatabaseInterface:
	
	def __init__(self):
		self.path=""
		self.db = []

	def openDatabase(self,uri):
		print("would open database: ", uri)
	def closeDatabase(self,uri):
		print("not implemented yet")
	def saveChanges(self,uri):
		print("not implemented yet")
	def readDatasetList(self):
		print("not implemented yet")
	def readDataset(self,datasetName):
		print("not implemented yet")
	def writeDataset(self):
		print("not implemented yet")
	
