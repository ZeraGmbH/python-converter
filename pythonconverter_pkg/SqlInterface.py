
from pythonconverter_pkg import DatabaseInterface as zdb
import json

class SqlInterface(zdb.DatabaseInterface):

	def __init__(self):
		self.sqlCommand = ""
		self.sqlResult = ""
		self.conn = []
		#self.c = pylint
		super().__init__()
		
	def openDatabase(self,uri):
		super().openDatabase(uri)

	def closeDatabase(self):
		print("close db not implemented yet")

	def readDatasetList(self, p_record):
		ret=""
		try:
			self.db.execute("SELECT transactions.transaction_name, transactions.contentset_names, transactions.guiContext_name ,transactions.start_time FROM sessions INNER JOIN transactions ON sessions.id = transactions.sessionid Where session_name=?", [p_record])
			ret=self.db.fetchall()
		except:
			print("is not a compatible database")
		return [dict(row) for row in ret]

	def readRecordList(self):
		ret=""
		try:
			self.db.execute("SELECT session_name FROM sessions")
			ret=self.db.fetchall()
		except:
			print("is not a compatible database")	
		return ret
		
	def readDataset(self,datasetName):
		ret=""
		try:
			self.db.execute("SELECT entities.entity_name, components.component_name, valuemap.component_value FROM transactions INNER JOIN transactions_valuemap ON transactions.id = transactions_valuemap.transactionsid INNER JOIN valuemap ON transactions_valuemap.valueid = valuemap.id INNER JOIN components ON valuemap.componentid = components.id INNER JOIN entities ON valuemap.entityiesid = entities.id WHERE transaction_name =?;", [datasetName])
			ret=self.db.fetchall()
		except:
			print("is not a compatible database")	
		return [dict(row) for row in ret]

	def dataSelect(self,selectString,selectVariables):
		self.db.execute(selectString,selectVariables)
		ret=self.db.fetchall()
		return [dict(row) for row in ret]

	def execute(self, command):
		print("not implemented yet")
	
	