
from datetime import datetime
import math
import numpy as np
import zeraconverterengines.Common as zeracom
import warnings
import logging
import json


class UserScript:
    
    def __init__(self):
        print("init Manipulation")
        self.__inputDict=dict()
        self.__outputDict=dict()
        # decimal places definition
        self.__dec=4
        self.__digits=8
        self.__local="EN"

        self.__convertDict = dict()
        funcMap=dict()
        funcMap["ZeraGuiActualValues"]=self.convertZeraGuiActualValues
        funcMap["ZeraGuiVectorDiagramm"]=self.convertZeraGuiVectorDiagramm
        funcMap["ZeraGuiPowerValues"]=self.convertZeraGuiPowerValues
        funcMap["ZeraGuiRMSValues"]=self.convertZeraGuiRMSValues

        self.__convertDict["ZeraActualValues"]=funcMap
        funcMap=dict()

        funcMap["ZeraGuiHarmonicTable"]=self.convertZeraGuiHarmonicTable
        funcMap["ZeraGuiHarmonicChart"]=self.convertZeraGuiHarmonicChart
        funcMap["ZeraGuiHarmonicPowerTable"]=self.convertZeraGuiHarmonicPowerTable
        funcMap["ZeraGuiHarmonicPowerChart"]=self.convertZeraGuiHarmonicPowerChart
        
        self.__convertDict["ZeraHarmonics"]=funcMap
        funcMap=dict()

        funcMap["ZeraGuiCurveDisplay"]=self.convertZeraGuiCurveDisplay
        self.__convertDict["ZeraCurves"]=funcMap
        funcMap=dict()

        funcMap["ZeraGuiMeterTest"]=self.convertZeraGuiMeterTest
        funcMap["ZeraGuiEnergyComparison"]=self.convertZeraGuiEnergyComparison
        funcMap["ZeraGuiEnergyRegister"]=self.convertZeraGuiEnergyRegister
        funcMap["ZeraGuiPowerRegister"]=self.convertZeraGuiPowerRegister

        self.__convertDict["ZeraComparison"]=funcMap
        funcMap=dict()

        funcMap["ZeraGuiVoltageBurden"]=self.convertZeraGuiVoltageBurden
        funcMap["ZeraGuiCurrentBurden"]=self.convertZeraGuiCurrentBurden

        self.__convertDict["ZeraBurden"]=funcMap
        funcMap=dict()

        funcMap["ZeraGuiInstrumentTransformer"]=self.convertZeraGuiInstrumentTransformer

        self.__convertDict["ZeraTransformer"]=funcMap
        funcMap=dict()

        funcMap["ZeraGuiCEDPower"]=self.convertZeraGuiCEDPower
        funcMap["ZeraGuiDCReference"]=self.convertZeraGuiDCReference

        self.__convertDict["ZeraDCReference"]=funcMap
        funcMap=dict()
        funcMap["ZeraAll"]=self.convertZeraAll
        self.__convertDict["ZeraAll"]=funcMap

        #print(self.__convertDict)

    def setInput(self, p_dict):
        self.__inputDict=p_dict
        return True

    def getOutput(self):
        return self.__outputDict

    def setParams(self,params):
        retVal=True
        try:
            if "digits" in params:
                self.__digits=int(params["digits"])
            if "decimalPlaces" in params:
                self.__dec=int(params["decimalPlaces"])
            if "local" in params:
                self.__local=params["local"]
        except:
            retVal=False
        return retVal

    def formatNumber(self,num):
        try:
            if type(num) == str:
                return num
            dec = self.__dec
            digitsTotal = self.__digits
            local= self.__local
            leadDigits=str(math.floor(abs(num)))
            if leadDigits == "0":
                leadDigits = ""
            preDecimals = len(leadDigits)
            if dec + preDecimals > digitsTotal:
                dec = digitsTotal - preDecimals
                if dec < 0:
                    dec = 0
            strNum =  str("{:."+str(dec)+"f}").format(num)
            if "de" in local:
                strNum=strNum.replace(".",",")
        except:
            strNum=str(num)
        return strNum

    def manipulate(self):
        retVal=True
        self.__outputDict["result-Data"]={"#childs" : []}
        retVal=self.iterateTransactions()
        return retVal

    def iterateTransactions(self):
        retVal=True
        device=dict()
        try:
            vals = zeracom.entityComponentSort(zeracom.getStatic(self.__inputDict))
            device["type"]=str(vals["StatusModule1"]["INF_DeviceType"])
            device["serial"]=str(vals["StatusModule1"]["PAR_SerialNr"])
        except:
            device["type"]="ZVP Device"
            device["serial"]="N/A"

        for session in self.__inputDict.keys(): 
            for key in self.__inputDict[session]["dynamic"].keys(): 
                if key.find("Snapshot") != -1:
                    contentSets=self.__inputDict[session]["dynamic"][key]["contentset_names"].split(",")
                    guiContext=self.__inputDict[session]["dynamic"][key]["guiContext"]
                    for content in self.__convertDict.keys():
                        if content in contentSets:
                            for guiCon in self.__convertDict[content].keys():
                                if guiCon == guiContext or content == "ZeraAll":
                                    try:
                                        if content == "ZeraAll":
                                            resList=self.__convertDict[content]["ZeraAll"](self.__inputDict[session]["dynamic"][key],{"session" : session, "transaction" : key, "device" : device})
                                        else:
                                            resList=self.__convertDict[content][guiCon](self.__inputDict[session]["dynamic"][key],{"session" : session, "transaction" : key,"device" : device})

                                        if type(resList) is list:
                                            for ele in resList:
                                                res=dict()
                                                res["Result"]=ele
                                                self.__outputDict["result-Data"]["#childs"].append(res)
                                        elif type(resList) is dict:
                                            res=dict()
                                            res["Result"]=resList
                                            self.__outputDict["result-Data"]["#childs"].append(res)
                                    except BaseException as err:
                                        logging.warning("Converting transaction "+key+" of type "+content+" failed with: "+str(err))
                                        retVal=False
        return retVal

    def TimeCommon(self,preadd,input):
        datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')
        eleList=list()
        time=""
        date=""
        if "en" in self.__local:
            time=datetimeObj.strftime("%H:%M:%S")
            date=datetimeObj.strftime("%m.%d.%Y")
        elif "de" in self.__local:
            time=datetimeObj.strftime("%H:%M:%S")
            date=datetimeObj.strftime("%H:%M:%S")
        else:
            time=datetimeObj.strftime("%H:%M:%S")
            date=datetimeObj.strftime("%m.%d.%Y")           
        eleList.append({"Time" : time})
        eleList.append({"Date" : preadd+date})
        return eleList


    def RangeCommon(self,input, metadata):
        vals=zeracom.entityComponentSort(input["values"])
        eleList=list()
        URange=float(0)
        IRange=float(0)
        for c in range(1,3):
            uDictVal=zeracom.UnitNumberSeperator(vals["RangeModule1"]["PAR_Channel"+ str(c)+"Range"])
            iDictVal=zeracom.UnitNumberSeperator(vals["RangeModule1"]["PAR_Channel"+ str(c+3)+"Range"])
            if URange < uDictVal["value"]:
                URange=uDictVal["value"]
            if IRange < iDictVal["value"]:
                IRange=iDictVal["value"]

        eleList.append({"U-Range" :  self.formatNumber(URange)+";"+uDictVal["unit"]})
        eleList.append({"I-Range" :  self.formatNumber(IRange)+";"+iDictVal["unit"]})
        return eleList

    def ActualValuesCommon(self,input, metadata):
        vals=zeracom.entityComponentSort(input["values"])
        eleList=list()
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : "DEU"})
        eleList.append({"Device-Typ" : metadata["device"]["type"]})
        eleList.append({"Device-No" : metadata["device"]["serial"]})    

        eleList.append({"U-PrimSek" : "1/1;V;1.00"})
        eleList.append({"I-PrimSek" : "1/1;A;1.00"})
        eleList.append({"PrimSek-Val-Cz-Reg" : "Off;Off;Off"})
        
        eleList.append(self.RangeCommon(input,metadata))

        UPN=list()

        UPN.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN1"].split(";")]))
        UPN.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN2"].split(";")]))
        UPN.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN3"].split(";")]))

        eleList.append({"UPN1" :  self.formatNumber(vals["RMSModule1"]["ACT_RMSPN1"])+";V"})
        eleList.append({"UPN2" :  self.formatNumber(vals["RMSModule1"]["ACT_RMSPN2"])+";V"})
        eleList.append({"UPN3" :  self.formatNumber(vals["RMSModule1"]["ACT_RMSPN3"])+";V"})

        eleList.append({"UPP12" :  self.formatNumber(vals["RMSModule1"]["ACT_RMSPP1"])+";V"})
        eleList.append({"UPP23" :  self.formatNumber(vals["RMSModule1"]["ACT_RMSPP2"])+";V"})
        eleList.append({"UPP31" :  self.formatNumber(vals["RMSModule1"]["ACT_RMSPP3"])+";V"})

        IL=list()

        #@TODO: is this 4,5,6 or 5,6,7 AUX channel
        IL.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN4"].split(";")]))
        IL.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN5"].split(";")]))
        IL.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN6"].split(";")]))

        eleList.append({"IL1" :  self.formatNumber(vals["RMSModule1"]["ACT_RMSPN4"])+";A"})
        eleList.append({"IL2" :  self.formatNumber(vals["RMSModule1"]["ACT_RMSPN5"])+";A"})
        eleList.append({"IL3" :  self.formatNumber(vals["RMSModule1"]["ACT_RMSPN6"])+";A"})

        eleList.append({"IDC1" : ""})
        eleList.append({"IDC2" : ""})
        eleList.append({"IDC3" : ""})

        eleList.append({"AU1" :  self.formatNumber(np.angle(np.complex(UPN[0][0],UPN[0][1]), deg=True))+";deg"})
        eleList.append({"AU2" :  self.formatNumber(np.angle(np.complex(UPN[1][0],UPN[1][1]), deg=True))+";deg"})
        eleList.append({"AU3" :  self.formatNumber(np.angle(np.complex(UPN[2][0],UPN[2][1]), deg=True))+";deg"})

        eleList.append({"AI1" :  self.formatNumber(np.angle(np.complex(IL[0][0],IL[0][1]), deg=True))+";deg"})
        eleList.append({"AI2" :  self.formatNumber(np.angle(np.complex(IL[1][0],IL[1][1]), deg=True))+";deg"})
        eleList.append({"AI3" :  self.formatNumber(np.angle(np.complex(IL[2][0],IL[2][1]), deg=True))+";deg"})
        
        # UI Angle per phase

        UI1=np.angle(np.complex(IL[0][0],IL[0][1]), deg=True)-np.angle(np.complex(UPN[0][0],UPN[0][1]), deg=True)
        UI2=np.angle(np.complex(IL[1][0],IL[1][1]), deg=True)-np.angle(np.complex(UPN[1][0],UPN[1][1]), deg=True)
        UI3=np.angle(np.complex(IL[2][0],IL[2][1]), deg=True)-np.angle(np.complex(UPN[2][0],UPN[2][1]), deg=True)

        eleList.append({"PHI1" :  self.formatNumber(UI1)+";deg"})
        eleList.append({"PHI2" :  self.formatNumber(UI2)+";deg"})
        eleList.append({"PHI3" :  self.formatNumber(UI3)+";deg"})
        
        eleList.append({"S1" :   self.formatNumber(vals["POWER1Module3"]["ACT_PQS1"])+";VA"})
        eleList.append({"S2" :   self.formatNumber(vals["POWER1Module3"]["ACT_PQS2"])+";VA"})
        eleList.append({"S3" :   self.formatNumber(vals["POWER1Module3"]["ACT_PQS3"])+";VA"})
        
        eleList.append({"P1" :  self.formatNumber(vals["POWER1Module1"]["ACT_PQS1"])+";W"})
        eleList.append({"P2" :  self.formatNumber(vals["POWER1Module1"]["ACT_PQS2"])+";W"})
        eleList.append({"P3" :  self.formatNumber(vals["POWER1Module1"]["ACT_PQS3"])+";W"})

        eleList.append({"Q1" :  self.formatNumber(vals["POWER1Module2"]["ACT_PQS1"])+";VAR"})
        eleList.append({"Q2" :  self.formatNumber(vals["POWER1Module2"]["ACT_PQS2"])+";VAR"})
        eleList.append({"Q3" :  self.formatNumber(vals["POWER1Module2"]["ACT_PQS3"])+";VAR"})

        
        SP=vals["POWER1Module1"]["ACT_PQS1"]+vals["POWER1Module1"]["ACT_PQS2"]+vals["POWER1Module1"]["ACT_PQS3"]
        SQ=vals["POWER1Module2"]["ACT_PQS1"]+vals["POWER1Module2"]["ACT_PQS2"]+vals["POWER1Module2"]["ACT_PQS3"]
        SS=vals["POWER1Module3"]["ACT_PQS1"]+vals["POWER1Module3"]["ACT_PQS2"]+vals["POWER1Module3"]["ACT_PQS3"]

        eleList.append({"SS" :  self.formatNumber(SS)+";VA"})
        eleList.append({"SP" :  self.formatNumber(SP)+";W"})
        eleList.append({"SQ" :  self.formatNumber(SQ)+";var"})
        
        eleList.append({"RF" : ""})
        eleList.append({"FREQ" :  self.formatNumber(vals["RangeModule1"]["ACT_Frequency"])})
        eleList.append({"UD1" : ""})
        eleList.append({"UD2" : ""})
        eleList.append({"UD3" : ""})
        eleList.append({"ID1" : ""})
        eleList.append({"ID2" : ""})
        eleList.append({"ID3" : ""})

        eleList.append({"AUX1" : ""})
        eleList.append({"AUX2" : ""})
        eleList.append({"AUX3" : ""})
        eleList.append({"AUX4" : ""})
        eleList.append({"AUX5" : ""})
        eleList.append({"AUX6" : ""})
        eleList.append({"AAUX1" : ""})
        eleList.append({"AAUX2" : ""})
        eleList.append({"AAUX3" : ""})
        eleList.append({"AAUX4" : ""})
        eleList.append({"AAUX5" : ""})
        eleList.append({"AAUX6" : ""})

        return eleList


    def LambdaCommon(self,input, metadata):
        vals=zeracom.entityComponentSort(input["values"])
        eleList=list()

        eleList.append({"Lambda1" :  self.formatNumber(vals["LambdaModule1"]["ACT_Lambda1"])})
        eleList.append({"Lambda2" :  self.formatNumber(vals["LambdaModule1"]["ACT_Lambda2"])})
        eleList.append({"Lambda3" :  self.formatNumber(vals["LambdaModule1"]["ACT_Lambda3"])})
        eleList.append({"SLambda" :  self.formatNumber(vals["LambdaModule1"]["ACT_Lambda4"])})

        return eleList

    def convertZeraGuiActualValues(self,input, metadata):
        endResult=list()
        result=dict()
        eleList=list()
        eleList.append({"Datatype" : "Actual-Values"})
        eleList.append({"Function" : "Value-Measurement"})

        eleList.append(self.TimeCommon("AV ",input))
        eleList.append(self.ActualValuesCommon(input,metadata))
        eleList.append(self.LambdaCommon(input,metadata))
        
        result["#childs"]=eleList
        endResult.append(result)
        return endResult



    def convertZeraGuiVectorDiagramm(self,input, metadata):
        endResult=list()
        result=dict()
        eleList=list()
        eleList.append(self.TimeCommon("VV ",input))
        eleList.append({"Datatype" : "Actual-Values"})
        eleList.append({"Function" : "Vector-Measurement"})
        eleList.append(self.ActualValuesCommon(input,metadata))
        eleList.append(self.LambdaCommon(input,metadata))
        
        
        result["#childs"]=eleList
        endResult.append(result)
        return endResult

    def convertZeraGuiPowerValues(self,input, metadata):
        return self.convertZeraGuiActualValues(input,metadata)

    def convertZeraGuiRMSValues(self,input, metadata):
        return self.convertZeraGuiActualValues(input,metadata)

    def convertZeraGuiHarmonicTable(self,input, metadata):
        vals=zeracom.entityComponentSort(input["values"])
        endresult=list()
        result=dict()
        eleList=list()
        channelMap=dict()
        channelMap["1"]=["U1","V"]
        channelMap["2"]=["U2","V"]
        channelMap["3"]=["U3","V"]
        channelMap["4"]=["I1","A"]
        channelMap["5"]=["I2","A"]
        channelMap["6"]=["I3","A"]
        channelMap["7"]=["UAUX","V"]
        channelMap["8"]=["IAUX","A"]


        for ch in range(1,9):
            result=dict()
            eleList=list()
            eleList.append({"ID" : metadata["session"]})
            eleList.append({"Language" : "DEU"})
            eleList.append({"Device-Typ" : metadata["device"]["type"]})
            eleList.append({"Device-No" : metadata["device"]["serial"]}) 
            eleList.append({"Function" : "Harmonics-Measurement"})
            eleList.append({"Datatype" : "Harmonic-Data"})
            NameAdd=""
            unit=""

            NameAdd=channelMap[str(ch)][0]
            unit=channelMap[str(ch)][1]
            eleList.append(self.TimeCommon("HT "+NameAdd+" ",input))

            eleList.append(self.RangeCommon(input,metadata))

            eleList.append({"U-PrimSek" : "1/1;U;1.00"})
            eleList.append({"I-PrimSek" : "1/1;A;1.00"})
            eleList.append({"M-Mode" : ""})
            eleList.append({"PrimSek-Val-Cz-Reg" : "Off;Off;Off"})
            eleList.append({"Channel" : NameAdd})
            
            if vals["THDNModule1"]["ACT_THDN"+ str(ch)] is not None:
                eleList.append({"Total-Harm" :  self.formatNumber(vals["THDNModule1"]["ACT_THDN"+ str(ch)])+";%"})

            count = 0
            i=0
            real = vals["FFTModule1"]["ACT_FFT"+ str(ch)].split(";")[2]
            imag = vals["FFTModule1"]["ACT_FFT"+ str(ch)].split(";")[3]
            baseAbs = np.linalg.norm(np.array([float(real),float(imag)]))
            baseAng = np.angle(np.complex(float(real),float(imag)), deg=True)
            for sample in vals["FFTModule1"]["ACT_FFT"+ str(ch)].split(";"):
                count = count + 1
                if count >= 2:
                    count = 0
                    imag = sample
                    val = np.array([float(real),float(imag)])
                    if i != 1:
                        eleList.append({"Harm" :  str(i)+";"+ self.formatNumber(np.linalg.norm(val)/baseAbs*100)+";%;"+ self.formatNumber(np.angle(np.complex(val[0],val[1]), deg=True))+";deg"})
                    else:
                        eleList.append({"Harm" :  str(i)+";"+self.formatNumber(baseAbs)+";"+unit+";"+self.formatNumber(baseAng)+";deg"})

                    i=i+1
                else:
                    real = sample

            result["#childs"]=eleList
            endresult.append(result)

        return endresult

    def convertZeraGuiHarmonicChart(self,input,metadata):
        return self.convertZeraGuiHarmonicTable(input,metadata)
        
        
        
    def convertZeraGuiCurveDisplay(self,input,metadata):
        vals=zeracom.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        endResult.append(result)
        
        for ch in range(1,5):
            result=dict()
            eleList=list()
            eleList.append({"ID" : metadata["session"]})
            eleList.append({"Language" : "DEU"})
            eleList.append({"Device-Typ" : metadata["device"]["type"]})
            eleList.append({"Device-No" : metadata["device"]["serial"]}) 
            eleList.append({"Function" : "Curve-Measurement"})
            eleList.append({"Datatype" : "Sample-Data"})

            eleList.append(self.TimeCommon("CD "+"UI "+str(ch)+" ",input))

            eleList.append({"U-PrimSek" : "1"})
            eleList.append({"I-PrimSek" : "1"})
            eleList.append({"M-Mode" : ""})
            eleList.append({"PrimSek-Val-Cz-Reg" : "Off;Off;Off"})

            eleList.append(self.RangeCommon(input,metadata))

            i=0    
            for sample in vals["OSCIModule1"]["ACT_OSCI"+ str(ch)].split(";"):
                i=i+1
                eleList.append({"SampleA" :  self.formatNumber(i)+";"+sample+";V"})

            eleList.append({"ChannelA" : "U"+ str(ch)})

            i=0    
            for sample in vals["OSCIModule1"]["ACT_OSCI"+ str(ch+4)].split(";"):
                i=i+1
                eleList.append({"SampleB" :  self.formatNumber(i)+";"+sample+";A"})

            eleList.append({"ChannelB" : "I"+ str(ch)})

            result["#childs"]=eleList
            endResult.append(result)
        
        
        return endResult




    def convertZeraGuiHarmonicPowerTable(self,input,metadata):
        vals=zeracom.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        

        for ch in range(1,4):
            result=dict()
            eleList=list()
            eleList.append({"ID" : metadata["session"]})
            eleList.append({"Language" : "DEU"})
            eleList.append({"Device-Typ" : metadata["device"]["type"]})
            eleList.append({"Device-No" : metadata["device"]["serial"]}) 
            eleList.append({"Function" : "Selektiv-Measurement"})
            eleList.append({"Datatype" : "Selektiv-Data"})

            eleList.append(self.TimeCommon("HP "+"UI"+ str(ch)+" ",input))

            eleList.append({"U-PrimSek" : "1/1;V;1.00"})
            eleList.append({"I-PrimSek" : "1/1;A;1.00"})
            eleList.append({"M-Mode" : ""})
            eleList.append({"PrimSek-Val-Cz-Reg" : "Off;Off;Off"})

            eleList.append(self.RangeCommon(input,metadata))
            

            eleList.append({"ChannelU" : "U"+ str(ch)})
            eleList.append({"ChannelI" : "I"+ str(ch)})

            for i in range(1,41):
                pqs=list()
                U=np.linalg.norm(np.array([float(vals["FFTModule1"]["ACT_FFT"+ str(ch)].split(";")[2*i-1]),float(vals["FFTModule1"]["ACT_FFT"+ str(ch)].split(";")[2*i])]))
                I=np.linalg.norm(np.array([float(vals["FFTModule1"]["ACT_FFT"+ str(ch+4)].split(";")[2*i-1]),float(vals["FFTModule1"]["ACT_FFT"+ str(ch+4)].split(";")[2*i])]))
                pqs.append(float(vals["Power3Module1"]["ACT_HPP"+ str(ch)].split(";")[i]))
                pqs.append(float(vals["Power3Module1"]["ACT_HPQ"+ str(ch)].split(";")[i]))
                pqs.append(float(vals["Power3Module1"]["ACT_HPS"+ str(ch)].split(";")[i]))
                eleList.append({"HarmValue" : "N;"+ self.formatNumber(i)+";U;"+ self.formatNumber(U)+";V;I;"+ self.formatNumber(I)+";A;P;"+ self.formatNumber(pqs[0])+";W;Q;"+ self.formatNumber(pqs[1])+";var;S;"+ self.formatNumber(pqs[2])+";VA"})

            result["#childs"]=eleList
            endResult.append(result)

        return endResult

    def convertZeraGuiHarmonicPowerChart(self,input,metadata):
        return self.convertZeraGuiHarmonicPowerTable(input,metadata)

    def convertZeraGuiMeterTest(self,input,metadata):
        vals=zeracom.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()

        eleList=self.ActualValuesCommon(input, metadata)
        eleList.append(self.LambdaCommon(input,metadata))
        eleList.append(self.TimeCommon("MT ",input))

        eleList.append({"Device-No" : metadata["device"]["serial"]}) 
        eleList.append({"AdjustData" : ""})
        eleList.append({"Function" : "Error-Measurement"})
        eleList.append({"Datatype" : "Meter-Error"})
        eleList.append({"Place-No" : "1"})

        mode=""
        if  self.formatNumber(vals["SEC1Module1"]["PAR_RefInput"]) == "P":
            mode=vals["POWER1Module1"]["PAR_MeasuringMode"]
        elif  self.formatNumber(vals["SEC1Module1"]["PAR_RefInput"]) == "Q":
            mode=vals["POWER1Module2"]["PAR_MeasuringMode"]
        elif  self.formatNumber(vals["SEC1Module1"]["PAR_RefInput"]) == "S":
            mode=vals["POWER1Module3"]["PAR_MeasuringMode"]
        eleList.append({"M-Mode" :  self.formatNumber(mode)})

        # eleList.append({"RF" : ""})
        eleList.append({"Cz" :  self.formatNumber(vals["SEC1Module1"]["PAR_DutConstant"])+";"+"x1"+";"+ self.formatNumber(vals["SEC1Module1"]["PAR_DUTConstUnit"])})
        eleList.append({"M-Puls" :  str(vals["SEC1Module1"]["PAR_MRate"])})
        eleList.append({"M-Inp" : self.formatNumber(vals["SEC1Module1"]["PAR_DutInput"])})
        eleList.append({"Error" :  self.formatNumber(vals["SEC1Module1"]["ACT_Result"])+"%"})
        multimeas=json.loads(vals["SEC1Module1"]["ACT_MulResult"])
        # maybe we should think about a totalCount in ACT_MulResult...
        totalCount = vals["SEC1Module1"]["ACT_MulCount"]
        if totalCount > 1:
            eleList.append({"N-Value" : str(totalCount)})
            eleList.append({"Spread" : self.formatNumber(multimeas["range"])+"%"})
            eleList.append({"Average" : self.formatNumber(multimeas["mean"])+"%"})
            eleList.append({"Deviation" : self.formatNumber(multimeas["stddevN1"])+"%"})
        else:
            eleList.append({"N-Value" : ""})
            eleList.append({"Spread" : ""})
            eleList.append({"Average" : ""})
            eleList.append({"Deviation" : ""})

        result["#childs"]=eleList
        return result

    def convertZeraGuiEnergyComparison(self,input, metadata):
        print("MtVis can not display Energy Comparison Data")

    def convertZeraGuiEnergyRegister(self,input,metadata):
        vals=zeracom.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : ""})
        eleList.append({"Device-Typ" : metadata["device"]["type"]})
        eleList.append({"Device-No" : metadata["device"]["serial"]}) 
        eleList.append({"AdjustData" : "ok"})
        datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')

        eleList.append(self.TimeCommon("ER ",input))
        
        eleList.append(self.RangeCommon(input,metadata))
        
        mode=""
        if  self.formatNumber(vals["SEM1Module1"]["PAR_RefInput"]) == "P":
            mode=vals["POWER1Module1"]["PAR_MeasuringMode"]
        elif  self.formatNumber(vals["SEM1Module1"]["PAR_RefInput"]) == "Q":
            mode=vals["POWER1Module2"]["PAR_MeasuringMode"]
        elif  self.formatNumber(vals["SEM1Module1"]["PAR_RefInput"]) == "S":
            mode=vals["POWER1Module3"]["PAR_MeasuringMode"]
        eleList.append({"M-Mode" :  self.formatNumber(mode)})
        eleList.append({"U-PrimSek" : "1/1;V;1.00"})
        eleList.append({"I-PrimSek" : "1/1;A;1.00"})
        eleList.append({"PrimSek-Val-Cz-Reg" : "Off;Off;Off"})
        eleList.append({"Function" : "Register-Test"})
        eleList.append({"Datatype" : "Register-Test"})
        eleList.append({"Place-No" : "1"})
        if vals["SEM1Module1"]["PAR_Targeted"] == 1:
            eleList.append({"Type" : "Duration"})        
        else:
            eleList.append({"Type" : "Start/Stop"})  
        eleList.append({"E-MTime" :  self.formatNumber(vals["SEM1Module1"]["ACT_Time"])+" s"}) # wird benötigt
        eleList.append({"Energie" :  self.formatNumber(vals["SEM1Module1"]["ACT_Energy"])+";"+ self.formatNumber(vals["SEM1Module1"]["PAR_TXUNIT"])})          # wird benötigt
        eleList.append({"E-Begin" :  self.formatNumber(vals["SEM1Module1"]["PAR_T0Input"])+";"+ self.formatNumber(vals["SEM1Module1"]["PAR_TXUNIT"])})    # wird benötigt
        eleList.append({"E-End" :  self.formatNumber(vals["SEM1Module1"]["PAR_T1input"])+";"+ self.formatNumber(vals["SEM1Module1"]["PAR_TXUNIT"])})      # wird benötigt
        eleList.append({"E-Cz" :  self.formatNumber(vals["SEM1Module1"]["PAR_TXUNIT"])})       # wird benötigt
        eleList.append({"E-Error" :  self.formatNumber(vals["SEM1Module1"]["ACT_Result"])+";%"})    # wird benötigt
        # eleList.append({"Power" : ""})      
        # eleList.append({"P-Begin" : ""})    
        # eleList.append({"P-End" : ""})      
        # eleList.append({"P-Cz" : ""})       
        # eleList.append({"P-Error" : ""})    

        result["#childs"]=eleList
        return result

    def convertZeraGuiPowerRegister(self,input, metadata):
        vals=zeracom.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : ""})
        eleList.append({"Device-Typ" : metadata["device"]["type"]})
        eleList.append({"Device-No" : metadata["device"]["serial"]}) 
        eleList.append({"AdjustData" : ""})

        eleList.append(self.TimeCommon("PR ",input))
        
        eleList.append(self.RangeCommon(input,metadata))
        
        mode = ""
        if  self.formatNumber(vals["SPM1Module1"]["PAR_RefInput"]) == "P":
            mode=vals["POWER1Module1"]["PAR_MeasuringMode"]
        elif  self.formatNumber(vals["SPM1Module1"]["PAR_RefInput"]) == "Q":
            mode=vals["POWER1Module2"]["PAR_MeasuringMode"]
        elif  self.formatNumber(vals["SPM1Module1"]["PAR_RefInput"]) == "S":
            mode=vals["POWER1Module3"]["PAR_MeasuringMode"]
        eleList.append({"M-Mode" :  self.formatNumber(mode)})
        eleList.append({"U-PrimSek" : "1/1;V;1.00"})
        eleList.append({"I-PrimSek" : "1/1;A;1.00"})
        eleList.append({"PrimSek-Val-Cz-Reg" : "Off;Off;Off"})
        eleList.append({"Function" : "Register-Test"})
        eleList.append({"Datatype" : "Register-Test"})
        eleList.append({"Place-No" : "1"})
        if vals["SPM1Module1"]["PAR_Targeted"] == 1:
            eleList.append({"Type" : "Duration"})        
        else:
            eleList.append({"Type" : "Start/Stop"})  
        eleList.append({"P-MTime" :  self.formatNumber(vals["SPM1Module1"]["ACT_Time"])+" s"}) # wird benötigt
        # eleList.append({"Energie" : ""})   
        # eleList.append({"E-Begin" : ""})    
        # eleList.append({"E-End" : ""})      
        # eleList.append({"E-Cz" : ""})       
        # eleList.append({"E-Error" : ""})    
        eleList.append({"Power" :  self.formatNumber(vals["SPM1Module1"]["ACT_Power"])+";"+ self.formatNumber(vals["SPM1Module1"]["PAR_TXUNIT"])})          # wird benötigt
        eleList.append({"P-Begin" :  self.formatNumber(vals["SPM1Module1"]["PAR_T0Input"])+";"+ self.formatNumber(vals["SPM1Module1"]["PAR_TXUNIT"])})    # wird benötigt
        eleList.append({"P-End" :  self.formatNumber(vals["SPM1Module1"]["PAR_T1input"])+";"+ self.formatNumber(vals["SPM1Module1"]["PAR_TXUNIT"])})      # wird benötigt
        eleList.append({"P-Cz" :  self.formatNumber(vals["SPM1Module1"]["PAR_TXUNIT"])})       # wird benötigt
        eleList.append({"P-Error" :  self.formatNumber(vals["SPM1Module1"]["ACT_Result"])+";%"})    # wird benötigt 

        result["#childs"]=eleList
        return result

    def convertZeraGuiVoltageBurden(self,input, metadata):
        vals=zeracom.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
       
        #eleList.append({"ID" : metadata["session"]})
        #eleList.append({"Language" : ""})
        #eleList.append({"Device-Typ" : metadata["device"]["type"]})
        #eleList.append({"Device-No" : metadata["device"]["serial"]}) 
        #eleList.append({"AdjustData" : ""})
        eleList=self.ActualValuesCommon(input, metadata)

        eleList.append(self.TimeCommon("VB ",input))

        #eleList.append(self.RangeCommon(input,metadata))

        eleList.append({"M-Mode" : ""})
        #eleList.append({"U-PrimSek" : "1/1;V;1.00"})
        #eleList.append({"I-PrimSek" : "1/1;A;1.00"})
        #eleList.append({"PrimSek-Val-Cz-Reg" : "Off;Off;Off"})
        eleList.append({"Function" : "U-Burden"})
        eleList.append({"Datatype" : "UBurden-Value"})
        eleList.append({"U-Nominal" :  self.formatNumber(vals["Burden1Module2"]["PAR_NominalRange"])+";V"}) 
        eleList.append({"B-Nominal" :  self.formatNumber(vals["Burden1Module2"]["PAR_NominalBurden"])+";VA"}) 
        eleList.append({"W-Length" :  self.formatNumber(vals["Burden1Module2"]["PAR_WireLength"])+";m"})   
        eleList.append({"W-Gauge" :  self.formatNumber(vals["Burden1Module2"]["PAR_WCrosssection"])+";mm2"})  
        

        result["#childs"]=eleList
        return result

    def convertZeraGuiCurrentBurden(self,input, metadata):
        vals=zeracom.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()

        #eleList.append({"ID" : metadata["session"]})
        #eleList.append({"Language" : ""})
        #eleList.append({"Device-Typ" : metadata["device"]["type"]})
        #eleList.append({"Device-No" : metadata["device"]["serial"]}) 
        #eleList.append({"AdjustData" : ""})
        eleList=self.ActualValuesCommon(input, metadata)

        eleList.append(self.TimeCommon("CB ",input))
        eleList.append({"M-Mode" : ""})
        #eleList.append(self.RangeCommon(input,metadata))
        #eleList.append({"U-PrimSek" : "1/1;V;1.00"})
        #eleList.append({"I-PrimSek" : "1/1;A;1.00"})
        #eleList.append({"PrimSek-Val-Cz-Reg" : "Off;Off;Off"})
        eleList.append({"Function" : "I-Burden"})
        eleList.append({"Datatype" : "IBurden-Value"})
        eleList.append({"I-Nominal" :  self.formatNumber(vals["Burden1Module1"]["PAR_NominalRange"])+";A"})  
        eleList.append({"B-Nominal" :   self.formatNumber(vals["Burden1Module1"]["PAR_NominalBurden"])+";VA"})  
        eleList.append({"W-Length" :   self.formatNumber(vals["Burden1Module1"]["PAR_WireLength"])+";m"})   
        eleList.append({"W-Gauge" :   self.formatNumber(vals["Burden1Module1"]["PAR_WCrosssection"])+";mm2"})
        

        result["#childs"]=eleList
        return result

    def convertZeraGuiInstrumentTransformer(self,input, metadata):
        vals=zeracom.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : "DEU"})
        eleList.append({"Device-Typ" : metadata["device"]["type"]})
        eleList.append({"Device-No" : metadata["device"]["serial"]}) 
        eleList.append({"AdjustData" : ""})

        eleList.append(self.TimeCommon("IT ",input))
        
        eleList.append(self.RangeCommon(input,metadata))
        
        eleList.append({"M-Mode" : ""})
        eleList.append({"U-PrimSek" : "1/1;V;1.00"})
        eleList.append({"I-PrimSek" : "1/1;A;1.00"})
        eleList.append({"PrimSek-Val-Cz-Reg" : "Off;Off;Off"})
        eleList.append({"Function" : "UI-Transformer"})
        eleList.append({"Datatype" : "UI-Transformer-Value"})
        # eleList.append({"VT-N" : ""})       
        # eleList.append({"VT-X" : ""})       
        # eleList.append({"U-Prim" : ""})     
        # eleList.append({"U-Sek-N" : ""})    
        # eleList.append({"U-Sek-X" : ""})    
        # eleList.append({"VT-Value" : ""})
        # eleList.append({"VT-Angle-deg" : ""})
        # eleList.append({"VT-Angle-min" : ""})
        # eleList.append({"VT-Angle-crad" : ""})
        eleList.append({"CT-N" :  self.formatNumber(vals["Transformer1Module1"]["PAR_PrimClampPrim"])+"/"+ self.formatNumber(vals["Transformer1Module1"]["PAR_PrimClampSec"])+";A"})
        eleList.append({"CT-X" :  self.formatNumber(vals["Transformer1Module1"]["PAR_DutPrimary"])+"/"+ self.formatNumber(vals["Transformer1Module1"]["PAR_DutSecondary"])+";A"})
        eleList.append({"CT_Xc" :  self.formatNumber(vals["Transformer1Module1"]["PAR_SecClampPrim"])+"/"+ self.formatNumber(vals["Transformer1Module1"]["PAR_SecClampSec"])+"/"+ self.formatNumber(vals["Transformer1Module1"]["PAR_DutSecondary"])+";A"})
        eleList.append({"I-Prim" :  self.formatNumber(vals["Transformer1Module1"]["ACT_IXPrimary1"])+";A"})     # wird benötigt
        eleList.append({"I-Sek-N" :  self.formatNumber(vals["Transformer1Module1"]["ACT_INSecondary1"])+";A"})     # wird benötigt
        eleList.append({"I-Sek-X" :  self.formatNumber(vals["Transformer1Module1"]["ACT_IXSecondary1"])+";A"})     # wird benötigt
        #@TODO XC is missing
        eleList.append({"CT-Value" :  self.formatNumber(vals["Transformer1Module1"]["ACT_Error1"])+";%"})
        eleList.append({"CT-Angle-deg" :  self.formatNumber(vals["Transformer1Module1"]["ACT_Angle1"])+";deg"})
        acrad=vals["Transformer1Module1"]["ACT_Angle1"]*math.pi/180*100
        amin=vals["Transformer1Module1"]["ACT_Angle1"]*60
        eleList.append({"CT-Angle-min" :  self.formatNumber(amin)+";min"})
        eleList.append({"CT-Angle-crad" :  self.formatNumber(acrad)+";crad"})
        # eleList.append({"VTCT-Value" : ""})
        # eleList.append({"VTCT-Angle-deg" : ""})
        # eleList.append({"VTCT-Angle-min" : ""})
        # eleList.append({"VTCT-Angle-crad" : ""})

        result["#childs"]=eleList
        return result

    def convertZeraGuiCEDPower(self,input, metadata):
        print("MtVis can not display CED Power Data")

    def convertZeraGuiDCReference(self,input, metadata):
        print("MtVis can not Display DC Reference Data")

    def convertZeraAll(self,input, metadata):
        endResult=list()
        funcList=list()
        funcList.append(self.convertZeraGuiActualValues)
        funcList.append(self.convertZeraGuiVectorDiagramm)
        funcList.append(self.convertZeraGuiHarmonicTable)
        funcList.append(self.convertZeraGuiMeterTest)
        funcList.append(self.convertZeraGuiEnergyRegister)
        funcList.append(self.convertZeraGuiPowerRegister)
        funcList.append(self.convertZeraGuiVoltageBurden)
        funcList.append(self.convertZeraGuiCurrentBurden)
        funcList.append(self.convertZeraGuiInstrumentTransformer)
        for func in funcList:
            try:
                ret=func(input,metadata)
                if type(ret) is list:
                    for ele in ret:
                        res=dict()
                        res=ele
                        endResult.append(res)
                elif type(ret) is dict:
                    res=dict()
                    res=ret
                    endResult.append(res)
            except BaseException as err:
                logging.warning("Converting transaction failed with: "+str(err))
                res=dict()

        return endResult

        
