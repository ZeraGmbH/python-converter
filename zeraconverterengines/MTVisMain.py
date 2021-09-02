import zeraconverterengines.Common as zeracom

class UserScript:
    def __init__(self):
        print("init Manipulation")
        self.__inputDict=dict()
        self.__outputDict=dict()

    def setInput(self, p_dict):
        self.__inputDict=p_dict

    def getOutput(self):
        return self.__outputDict

    def setParams(self,params):
        return

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
        vals = zeracom.entityComponentSort(zeracom.getStatic(self.__inputDict))
        eleList.append({"ID" : id[0]})
        eleList.append({"State" : "exported"})
        eleList.append({"Remark" : str(vals["CustomerData"]["PAR_DatasetComment"])})
        general["General"]={"#childs" : eleList}
        eleList=list()
        eleList.append({"Firstname" : vals["CustomerData"]["PAR_CustomerFirstName"]})
        eleList.append({"Name" : vals["CustomerData"]["PAR_CustomerLastName"]})
        eleList.append({"Street" : vals["CustomerData"]["PAR_CustomerStreet"]})
        eleList.append({"Postcode" : str(vals["CustomerData"]["PAR_CustomerPostalCode"])})
        eleList.append({"City" : vals["CustomerData"]["PAR_CustomerCity"]})
        eleList.append({"Country" : vals["CustomerData"]["PAR_CustomerCountry"]})
        eleList.append({"No" : str(vals["CustomerData"]["PAR_CustomerNumber"])})
        eleList.append({"Remark" : str(vals["CustomerData"]["PAR_CustomerComment"])})
        customer["Customer"]={"#childs" : eleList}
        eleList=list()
        eleList.append({"Firstname" : vals["CustomerData"]["PAR_LocationFirstName"]})
        eleList.append({"Name" : vals["CustomerData"]["PAR_LocationLastName"]})
        eleList.append({"Street" : vals["CustomerData"]["PAR_LocationStreet"]})
        eleList.append({"Postcode" : str(vals["CustomerData"]["PAR_LocationPostalCode"])})
        eleList.append({"City" : vals["CustomerData"]["PAR_LocationCity"]})
        eleList.append({"Country" : vals["CustomerData"]["PAR_LocationCountry"]})
        eleList.append({"No" : str(vals["CustomerData"]["PAR_LocationNumber"])})
        eleList.append({"Remark" : str(vals["CustomerData"]["PAR_LocationComment"])})
        location["Location"]={"#childs" : eleList}
        eleList=list()

        eleList.append({"Operator" : vals["CustomerData"]["PAR_PowerGridOperator"]})
        eleList.append({"Supplier" : vals["CustomerData"]["PAR_PowerGridSupplier"]})
        eleList.append({"Remark" : str(vals["CustomerData"]["PAR_PowerGridComment"])})
        net["Net"]={"#childs" : eleList}
        eleList=list()

        eleList.append({"Manufacturer" : vals["CustomerData"]["PAR_MeterManufacturer"]})
        eleList.append({"Manuf-No" : str(vals["CustomerData"]["PAR_MeterFactoryNumber"])})
        eleList.append({"Custom-No" : str(vals["CustomerData"]["PAR_MeterOwner"])})
        eleList.append({"Remark" : str(vals["CustomerData"]["PAR_MeterComment"])})
        meter["Meter"]={"#childs" : eleList}

        main=dict()
        main["Main"]={"#childs" : [{}]}

        main["Main"]["#childs"].append(general)
        main["Main"]["#childs"].append(customer)
        main["Main"]["#childs"].append(location)
        main["Main"]["#childs"].append(net)
        main["Main"]["#childs"].append(meter)
        self.__outputDict["Main-Data"]["#childs"].append(main)
        return 0

