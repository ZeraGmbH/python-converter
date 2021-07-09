import sqlite3
from sqlite3 import Error

from pythonconverter_pkg import SqlInterface as zsq

class SqlLiteInterface(zsq.SqlInterface):
    def __init__(self):
        print("init sqlite interface")
        super().__init__()
    
    def openDatabase(self,uri):
        self.file=uri
        try:
            self.conn = sqlite3.connect(uri)
            self.conn.row_factory = sqlite3.Row
            self.db=self.conn.cursor()
        except sqlite3.Error:
            print("db error")
        return 1
        
    def closeDatabase(self):
        self.conn.close()

    def execute(self, command):
        self.db.execute(command)
        ret=self.db.fetchall()
        print(ret)
    
    def save(self):
        return 0
        
    def result(self):
        return 0
    
