
from datetime import datetime
import math
import numpy as np

class UserScript:
    def __init__(self):
        print("init Manipulation")
        self.__inputDict=dict()
        self.__outputDict=dict()


    def testFunc(self):
        print("Mapped function called")


    def setInput(self, p_dict):
        self.__inputDict=p_dict

    def getOutput(self):
        return self.__outputDict

    def manipulate(self):
        print("manipultate")
        self.__outputDict["Main-Data"]={"#childs" : [{}]}
        
        eleList=list()
        general=dict()
        customer=dict()
        location=dict()
        net=dict()
        meter=dict()
        id = [k  for  k in self.__inputDict.keys()]
        eleList.append({"ID" : id[0]})
        eleList.append({"State" : ""})
        eleList.append({"Remark" : ""})
        general["General"]={"#childs" : eleList}
        eleList=list()
        eleList.append({"Firstname" : ""})
        eleList.append({"Name" : ""})
        eleList.append({"Street" : ""})
        eleList.append({"Postcode" : ""})
        eleList.append({"City" : ""})
        eleList.append({"Country" : ""})
        eleList.append({"No" : ""})
        eleList.append({"Remark" : ""})
        customer["Customer"]={"#childs" : eleList}
        eleList=list()
        eleList.append({"Firstname" : ""})
        eleList.append({"Name" : ""})
        eleList.append({"Street" : ""})
        eleList.append({"Postcode" : ""})
        eleList.append({"City" : ""})
        eleList.append({"Country" : ""})
        eleList.append({"No" : ""})
        eleList.append({"Remark" : ""})
        location["Location"]={"#childs" : eleList}
        eleList=list()

        eleList.append({"Operator" : ""})
        eleList.append({"Supplier" : ""})
        eleList.append({"Remark" : ""})
        net["Net"]={"#childs" : eleList}
        eleList=list()

        eleList.append({"Manufacturer" : ""})
        eleList.append({"Manuf-No" : ""})
        eleList.append({"Custom-No" : ""})
        eleList.append({"Remark" : ""})
        meter["Meter"]={"#childs" : eleList}

        main=dict()
        main["Main"]={"#childs" : [{}]}

        main["Main"]["#childs"].append(general)
        main["Main"]["#childs"].append(customer)
        main["Main"]["#childs"].append(location)
        main["Main"]["#childs"].append(net)
        main["Main"]["#childs"].append(meter)
        self.__outputDict["Main-Data"]["#childs"].append(main)
        

        #dicto["result-Data"]={"@id" : "1", "#childs" : [{"item1" : {"@id" : "3", "#text" : "test3"}}, {"item1" : "test2"}]}

    