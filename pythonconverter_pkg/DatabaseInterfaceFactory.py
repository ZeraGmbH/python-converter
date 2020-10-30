from pythonconverter_pkg import SqlLite3Interface as zsq
from pythonconverter_pkg import XmlInterface as zxml

class DatabaseInterfaceFactory:
    def __init__(self):
        print("init DatabaseInterfaceFactory")

    def InputInterface(self, type):
        return zsq.SqlLiteInterface()

    def OutputInterface(self,type):
         return  zxml.XmlInterface()