from datetime import datetime
import math
import logging
import json
import numpy as np
import zeraconverterengines.Common as zeracom

class UserScript:

    def __init__(self):
        print("init Manipulation")
        self.__inputDict={}
        self.__outputDict={}
        # decimal places definition
        self.__dec=4
        self.__digits=8
        self.__local="EN"

        self.__convertDict = {}
        funcMap={}
        funcMap["ZeraGuiActualValues"]=self.convertZeraGuiActualValues
        funcMap["ZeraGuiVectorDiagramm"]=self.convertZeraGuiVectorDiagramm
        funcMap["ZeraGuiPowerValues"]=self.convertZeraGuiPowerValues
        funcMap["ZeraGuiRMSValues"]=self.convertZeraGuiRMSValues

        self.__convertDict["ZeraActualValues"]=funcMap
        funcMap={}

        funcMap["ZeraGuiHarmonicTable"]=self.convertZeraGuiHarmonicTable
        funcMap["ZeraGuiHarmonicChart"]=self.convertZeraGuiHarmonicChart
        funcMap["ZeraGuiHarmonicPowerTable"]=self.convertZeraGuiHarmonicPowerTable
        funcMap["ZeraGuiHarmonicPowerChart"]=self.convertZeraGuiHarmonicPowerChart

        self.__convertDict["ZeraHarmonics"]=funcMap
        funcMap={}

        funcMap["ZeraGuiCurveDisplay"]=self.convertZeraGuiCurveDisplay
        self.__convertDict["ZeraCurves"]=funcMap
        funcMap={}

        funcMap["ZeraGuiMeterTest"]=self.convertZeraGuiMeterTest
        funcMap["ZeraGuiEnergyComparison"]=self.convertZeraGuiEnergyComparison
        funcMap["ZeraGuiEnergyRegister"]=self.convertZeraGuiEnergyRegister
        funcMap["ZeraGuiPowerRegister"]=self.convertZeraGuiPowerRegister

        self.__convertDict["ZeraComparison"]=funcMap
        funcMap={}

        funcMap["ZeraGuiVoltageBurden"]=self.convertZeraGuiVoltageBurden
        funcMap["ZeraGuiCurrentBurden"]=self.convertZeraGuiCurrentBurden

        self.__convertDict["ZeraBurden"]=funcMap
        funcMap={}

        funcMap["ZeraGuiInstrumentTransformer"]=self.convertZeraGuiInstrumentTransformer

        self.__convertDict["ZeraTransformer"]=funcMap
        funcMap={}

        funcMap["ZeraGuiCEDPower"]=self.convertZeraGuiCEDPower
        funcMap["ZeraGuiDCReference"]=self.convertZeraGuiDCReference

        self.__convertDict["ZeraDCReference"]=funcMap
        funcMap={}
        funcMap["ZeraAll"]=self.convertZeraAll
        self.__convertDict["ZeraAll"]=funcMap

        self.__convertDict["ZeraQuartzReference"]={}

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

    def setScale(self, factor, unitPrefix, scaleInfo):
        scaleInfo["factor"] = factor
        scaleInfo["unitPrefix"] = unitPrefix

    def scaleSingleValForPrefix(self, absValue, factor, unitPrefix, scaleInfo):
        scaled = False
        limit = 1 / factor
        if(absValue >= limit):
            self.setScale(factor, unitPrefix, scaleInfo)
            scaled = True
        return scaled

    scaleFactors = {
        "P": 1e-15,
        "T": 1e-12,
        "G": 1e-9,
        "M": 1e-6,
        "k": 1e-3,
        "": 1,
        "m": 1e3
    }

    def scaleSingleVal(self, value, scaleInfo):
        absValue = math.fabs(value)
        if(self.scaleSingleValForPrefix(absValue, UserScript.scaleFactors["P"], "P", scaleInfo)):
            return
        if(self.scaleSingleValForPrefix(absValue, UserScript.scaleFactors["T"], "T", scaleInfo)):
            return
        if(self.scaleSingleValForPrefix(absValue, UserScript.scaleFactors["G"], "G", scaleInfo)):
            return
        if(self.scaleSingleValForPrefix(absValue, UserScript.scaleFactors["M"], "M", scaleInfo)):
            return
        if(self.scaleSingleValForPrefix(absValue, UserScript.scaleFactors["k"], "k", scaleInfo)):
            return
        if(self.scaleSingleValForPrefix(absValue, UserScript.scaleFactors[""], "", scaleInfo)):
            return
        self.setScale(UserScript.scaleFactors["m"], "m", scaleInfo)
        return

    def computeScaling(self, paramValues, scaleInfo):
        maxAbsVal = 0.0
        for value in paramValues:
            absValue = math.fabs(value)
            if(absValue > maxAbsVal):
                maxAbsVal = absValue
        return self.scaleSingleVal(maxAbsVal, scaleInfo)

    def alignDecSeparator(self, strNum):
        if "DE" in self.__local.upper():
            strNum = strNum.replace(".",",")
        return strNum

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
            strNum = str("{:."+str(dec)+"f}").format(num)
            strNum = self.alignDecSeparator(strNum)
        except:
            strNum=str(num)
        return strNum

    def formatAngle(self, num):
        if type(num) == str:
            return num
        if num < 0:
            num = num + 360
        return self.formatNumber(num)

    def ms_to_hh_mm_ss(self, milliseconds):
        if(milliseconds == ""):
            seconds = 0
        else:
            secondsexact = milliseconds / 1000
            seconds = round(secondsexact)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def manipulate(self):
        retVal=0
        self.__outputDict["Result-Data"]={"#childs" : []}
        retVal=self.iterateTransactions()
        return retVal

    def iterateTransactions(self):
        retVal=0
        device={}
        try:
            vals = zeracom.entityComponentSort(zeracom.getStatic(self.__inputDict))
            device["type"]=str(zeracom.readSafe(vals,["StatusModule1","INF_DeviceType"]))
            device["serial"]=str(zeracom.readSafe(vals,["StatusModule1","PAR_SerialNr"]))
        except:
            device["type"]="ZVP Device"
            device["serial"]="N/A"

        for session in self.__inputDict.keys():

            for key in self.__inputDict[session]["dynamic"].keys():

                if key.find("Snapshot") != -1:
                    contentSets=self.__inputDict[session]["dynamic"][key]["contentset_names"].split(",")
                    guiContext=self.__inputDict[session]["dynamic"][key]["guiContext"]
                    for content in contentSets:
                        if content in self.__convertDict.keys():
                            if guiContext in self.__convertDict[content].keys() or content == "ZeraAll":
                                try:
                                    if content == "ZeraAll":
                                        resList=self.__convertDict[content]["ZeraAll"](self.__inputDict[session]["dynamic"][key],{"session" : session, "transaction" : key, "device" : device})
                                    else:
                                        resList=self.__convertDict[content][guiContext](self.__inputDict[session]["dynamic"][key],{"session" : session, "transaction" : key,"device" : device})

                                    if type(resList) is list:
                                        for ele in resList:
                                            res={}
                                            res["Result"]=ele
                                            self.__outputDict["Result-Data"]["#childs"].append(res)
                                    elif type(resList) is dict:
                                        res={}
                                        res["Result"]=resList
                                        self.__outputDict["Result-Data"]["#childs"].append(res)
                                except BaseException as err:
                                    logging.warning("Converting transaction "+key+" of type "+content+" failed with: "+str(err))
                                    retVal=retVal | 2
                            else:
                                #retVal=retVal | 4 # Custom conttent will always have this issue
                                logging.warning("Unknown guicontext for content: " + guiContext)
                        else:
                            retVal=retVal | 4
                            logging.warning("Unknown content type : " + content)
        return retVal

    def TimeCommon(self,preadd,compList):
        datetimeObj= datetime.strptime(compList["timestemp"], '%a %b %d %H:%M:%S %Y')
        eleList=[]
        time=""
        date=""
        if "en" in self.__local:
            time=datetimeObj.strftime("%H:%M:%S")
            date=datetimeObj.strftime("%m.%d.%Y")
        elif "de" in self.__local:
            time=datetimeObj.strftime("%H:%M:%S")
            date=datetimeObj.strftime("%d.%m.%Y")
        else:
            time=datetimeObj.strftime("%H:%M:%S")
            date=datetimeObj.strftime("%m.%d.%Y")

        eleList.append({"Time" : time})
        eleList.append({"Date" : preadd+date})
        return eleList

    def MtVisUnitAdjust(self, valUnitStr):
        valUnitObj = zeracom.UnitNumberSeperator(valUnitStr)
        unit = valUnitObj["unit"]
        if unit.startswith("m"):
            valUnitObj["unit"] = unit.replace("m", "")
            valUnitObj["value"] = valUnitObj["value"] / 1000
        strValue = "{:g}".format(valUnitObj["value"])
        return  strValue + valUnitObj["unit"]

    def RangeCommon(self, compList, mtvisRange = False):
        #pylint: disable=unused-argument
        vals=zeracom.entityComponentSort(compList["values"])
        eleList=[]
        URange=float(0)
        IRange=float(0)
        uRangeExported = ""
        iRangeExported = ""
        if not self.IsEmobDcSession(vals):
            uMaxRangeStr = ""
            iMaxRangeStr = ""
            for c in range(1, 3+1): # confusing but checkout https://www.w3schools.com/python/python_for_loops.asp
                uRawValue = zeracom.readSafe(vals,["RangeModule1", "PAR_Channel"+ str(c)+"Range"])
                uDictVal = zeracom.UnitNumberSeperator(uRawValue)
                if URange < uDictVal["value"]:
                    URange = uDictVal["value"]
                    uMaxRangeStr = uRawValue
                iRawValue = zeracom.readSafe(vals,["RangeModule1", "PAR_Channel"+ str(c+3)+"Range"])
                iDictVal = zeracom.UnitNumberSeperator(iRawValue)
                if IRange < iDictVal["value"]:
                    IRange = iDictVal["value"]
                    iMaxRangeStr = iRawValue

            uRangeExported = uMaxRangeStr
            iRangeExported = iMaxRangeStr
        else:
            uRangeExported = zeracom.readSafe(vals,["RangeModule1","PAR_Channel7Range"])
            iRangeExported = zeracom.readSafe(vals,["RangeModule1","PAR_Channel8Range"])

        if mtvisRange:
            uRangeExported = self.alignDecSeparator(self.MtVisUnitAdjust(uRangeExported))
            iRangeExported = self.alignDecSeparator(self.MtVisUnitAdjust(iRangeExported))
        eleList.append({"U-Range" : uRangeExported + ";"})
        eleList.append({"I-Range" : iRangeExported + ";"})
        return eleList

    def ScaleCommon(self,compList, metadata):
        vals=zeracom.entityComponentSort(compList["values"])
        eleList=[]

        uPrimSec=zeracom.readSafe(vals,["RangeModule1","PAR_PreScalingGroup0"])+";V;1.00"
        iPrimSec=zeracom.readSafe(vals,["RangeModule1","PAR_PreScalingGroup1"])+";A;1.00"
        ActScaleEnabled="OFF"
        DutScaleEnabled="OFF"
        if(zeracom.readSafe(vals,["RangeModule1","PAR_PreScalingEnabledGroup0"]) == 1):
            ActScaleEnabled="ON"
        if(zeracom.readSafe(vals,["RangeModule1","PAR_PreScalingEnabledGroup1"]) == 1):
            ActScaleEnabled="ON"
        if "SEC1Module1" in vals:
            testMode=zeracom.readSafe(vals,["SEC1Module1","PAR_DutTypeMeasurePoint"])
            if(testMode != "CpIpUp" and testMode != "CsIsUs" and testMode != ""):
                DutScaleEnabled="ON"

        eleList.append({"U-PrimSek" : uPrimSec})
        eleList.append({"I-PrimSek" : iPrimSec})
        eleList.append({"PrimSek-Val-Cz-Reg" : ActScaleEnabled+";"+DutScaleEnabled+";Off"})
        return eleList

    def SessionDeviceInfo(self, metadata, Language):
        eleList=[]
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : Language})
        eleList.append({"Device-Typ" : metadata["device"]["type"]})
        eleList.append({"Device-No" : metadata["device"]["serial"]})
        return eleList
    
    def IsEmobDcSession(self, vals):
        isEmobDc = False
        if "SEC1Module1" in vals: # currently we have no better for EMOB DC
            isEmobDc = zeracom.readSafe(vals,["SEC1Module1","PAR_RefInput"]) == "P DC"
        return isEmobDc

    def CurrentBurdenValues (self, compList):
        vals=zeracom.entityComponentSort(compList["values"])
        eleList=[]

        eleList.append({"Sb1" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","ACT_Burden1"]))+";VA"})
        eleList.append({"Sb2" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","ACT_Burden2"]))+";VA"})
        eleList.append({"Sb3" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","ACT_Burden3"]))+";VA"})
        
        eleList.append({"CosBeta1" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","ACT_PFactor1"]))+";"})
        eleList.append({"CosBeta2" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","ACT_PFactor2"]))+";"})
        eleList.append({"CosBeta3" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","ACT_PFactor3"]))+";"})
        
        eleList.append({"SN1" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","ACT_Ratio1"]))+";%"})
        eleList.append({"SN2" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","ACT_Ratio2"]))+";%"})
        eleList.append({"SN3" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","ACT_Ratio3"]))+";%"})
         
        return eleList

    def VoltageBurdenValues (self, compList):
        vals=zeracom.entityComponentSort(compList["values"])
        eleList=[]

        eleList.append({"Sb1" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","ACT_Burden1"]))+";VA"})
        eleList.append({"Sb2" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","ACT_Burden2"]))+";VA"})
        eleList.append({"Sb3" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","ACT_Burden3"]))+";VA"})

        eleList.append({"CosBeta1" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","ACT_PFactor1"]))+";"})
        eleList.append({"CosBeta2" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","ACT_PFactor2"]))+";"})
        eleList.append({"CosBeta3" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","ACT_PFactor3"]))+";"})

        eleList.append({"SN1" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","ACT_Ratio1"]))+";%"})
        eleList.append({"SN2" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","ACT_Ratio2"]))+";%"})
        eleList.append({"SN3" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","ACT_Ratio3"]))+";%"})
        
        return eleList 

    def UPNRmsValues(self, compList, vectorMeasurement):
        vals=zeracom.entityComponentSort(compList["values"])
        scaleInfo = {
            "factor": 0.0,
            "unitPrefix": ""
        }
        eleList=[]

        if not self.IsEmobDcSession(vals):
            rowValues=[zeracom.readSafe(vals,["RMSModule1","ACT_RMSPN1"]),
                    zeracom.readSafe(vals,["RMSModule1","ACT_RMSPN2"]),
                    zeracom.readSafe(vals,["RMSModule1","ACT_RMSPN3"])]
        else:
            rowValues=[zeracom.readSafe(vals,["FFTModule1","ACT_DC7"]),
                    0,
                    0]

        if vectorMeasurement:
            # Here we remove prescaling factor from RMS value to get original unscaled RMS value back and make unit of UPN1..3 same as unit of 'U-Range'.
            # Currently used only for vector diagram
            scaleInfo["factor"] = zeracom.readSafe(vals,["RangeModule1","INF_PreScalingInfoGroup0"]) #un-prescale RMS value
            voltageRange = self.RangeCommon(compList)[0]["U-Range"].replace(";", "") #If 'U-Range' is '250V;' make it '250V'
            voltageRangeUnitPrefix = zeracom.UnitNumberSeperator(voltageRange)["unit"].replace("V", "") #we are interested in just unit-prefix
            scaleInfo["factor"] *= self.scaleFactors[voltageRangeUnitPrefix] #scale to fit to new unit
            scaleInfo["unitPrefix"] = voltageRangeUnitPrefix
        else:
            self.computeScaling(rowValues, scaleInfo)
        eleList.append({"UPN1" :  self.formatNumber(rowValues[0]*scaleInfo["factor"])+";" + scaleInfo["unitPrefix"] + "V"})
        eleList.append({"UPN2" :  self.formatNumber(rowValues[1]*scaleInfo["factor"])+";" + scaleInfo["unitPrefix"] + "V"})
        eleList.append({"UPN3" :  self.formatNumber(rowValues[2]*scaleInfo["factor"])+";" + scaleInfo["unitPrefix"] + "V"})
        return eleList

    def IValues(self, compList, vectorMeasurement):
        vals=zeracom.entityComponentSort(compList["values"])
        scaleInfo = {
            "factor": 0.0,
            "unitPrefix": ""
        }
        eleList=[]

        if not self.IsEmobDcSession(vals):
            rowValues=[zeracom.readSafe(vals,["RMSModule1","ACT_RMSPN4"]),
                    zeracom.readSafe(vals,["RMSModule1","ACT_RMSPN5"]),
                    zeracom.readSafe(vals,["RMSModule1","ACT_RMSPN6"])]
        else:
            rowValues=[zeracom.readSafe(vals,["FFTModule1","ACT_DC8"]),
                    0,
                    0]

        if vectorMeasurement:
            # Here we remove prescaling factor from RMS value to get original unscaled RMS value back and make unit of IL1..3 same as unit of 'I-Range'.
            # Currently used only for vector diagram
            scaleInfo["factor"] = zeracom.readSafe(vals,["RangeModule1","INF_PreScalingInfoGroup1"]) #un-prescale RMS value
            currentRange = self.RangeCommon(compList)[1]["I-Range"].replace(";", "") #If 'I-Range' is '100mA;' make it '100mA'
            currentRangeUnitPrefix = zeracom.UnitNumberSeperator(currentRange)["unit"].replace("A", "") #we are interested in just unit-prefix
            scaleInfo["factor"] *= self.scaleFactors[currentRangeUnitPrefix] #scale to fit to new unit
            scaleInfo["unitPrefix"] = currentRangeUnitPrefix
        else:
            self.computeScaling(rowValues, scaleInfo)
        eleList.append({"IL1" :  self.formatNumber(rowValues[0]*scaleInfo["factor"])+";" + scaleInfo["unitPrefix"] + "A"})
        eleList.append({"IL2" :  self.formatNumber(rowValues[1]*scaleInfo["factor"])+";" + scaleInfo["unitPrefix"] + "A"})
        eleList.append({"IL3" :  self.formatNumber(rowValues[2]*scaleInfo["factor"])+";" + scaleInfo["unitPrefix"] + "A"})

        return eleList

    def UPNDftValues(self, compList):
        vals=zeracom.entityComponentSort(compList["values"])
        UPN=[]

        UPN.append(np.array([float(i) for i in zeracom.readSafe(vals,["DFTModule1","ACT_DFTPN1"]).split(";")]))
        UPN.append(np.array([float(i) for i in zeracom.readSafe(vals,["DFTModule1","ACT_DFTPN2"]).split(";")]))
        UPN.append(np.array([float(i) for i in zeracom.readSafe(vals,["DFTModule1","ACT_DFTPN3"]).split(";")]))

        return UPN

    def IDftValues(self, compList):
        vals=zeracom.entityComponentSort(compList["values"])
        IL=[]

        #@TODO: is this 4,5,6 or 5,6,7 AUX channel
        IL.append(np.array([float(i) for i in zeracom.readSafe(vals,["DFTModule1","ACT_DFTPN4"]).split(";")]))
        IL.append(np.array([float(i) for i in zeracom.readSafe(vals,["DFTModule1","ACT_DFTPN5"]).split(";")]))
        IL.append(np.array([float(i) for i in zeracom.readSafe(vals,["DFTModule1","ACT_DFTPN6"]).split(";")]))
        
        return IL

    def UIPhaseAngleValues(self, compList):
        vals=zeracom.entityComponentSort(compList["values"])
        eleList=[]

        UPN=self.UPNDftValues(compList)
        IL=self.IDftValues(compList)
        UI1=np.angle(complex(IL[0][0],IL[0][1]), deg=True)-np.angle(complex(UPN[0][0],UPN[0][1]), deg=True)
        UI2=np.angle(complex(IL[1][0],IL[1][1]), deg=True)-np.angle(complex(UPN[1][0],UPN[1][1]), deg=True)
        UI3=np.angle(complex(IL[2][0],IL[2][1]), deg=True)-np.angle(complex(UPN[2][0],UPN[2][1]), deg=True)
        
        eleList.append({"PHI1" :  self.formatNumber(UI1)+";deg"})
        eleList.append({"PHI2" :  self.formatNumber(UI2)+";deg"})
        eleList.append({"PHI3" :  self.formatNumber(UI3)+";deg"})

        return eleList

    def ActualValuesCommon(self,compList, metadata, vectorMeasurement):
        vals=zeracom.entityComponentSort(compList["values"])
        scaleInfo = {
            "factor": 0.0,
            "unitPrefix": ""
        }

        eleList=[]
        eleList.append(self.SessionDeviceInfo(metadata, 'DEU'))
        eleList.append(self.ScaleCommon(compList, metadata))

        eleList.append(self.RangeCommon(compList))
        
        eleList.append(self.UPNRmsValues(compList, vectorMeasurement))

        is_dc = self.IsEmobDcSession(vals)
        if not is_dc:
            rowValues=[zeracom.readSafe(vals,["RMSModule1","ACT_RMSPP1"]),
                    zeracom.readSafe(vals,["RMSModule1","ACT_RMSPP2"]),
                    zeracom.readSafe(vals,["RMSModule1","ACT_RMSPP3"])]
            self.computeScaling(rowValues, scaleInfo)
            eleList.append({"UPP12" :  self.formatNumber(rowValues[0]*scaleInfo["factor"])+";" + scaleInfo["unitPrefix"] + "V"})
            eleList.append({"UPP23" :  self.formatNumber(rowValues[1]*scaleInfo["factor"])+";" + scaleInfo["unitPrefix"] + "V"})
            eleList.append({"UPP31" :  self.formatNumber(rowValues[2]*scaleInfo["factor"])+";" + scaleInfo["unitPrefix"] + "V"})

        eleList.append(self.IValues(compList, vectorMeasurement))
        
        eleList.append({"IDC1" : ""})
        eleList.append({"IDC2" : ""})
        eleList.append({"IDC3" : ""})

        if not is_dc:
            UPN=self.UPNDftValues(compList)
            IL=self.IDftValues(compList)

            eleList.append({"AU1" :  self.formatAngle(np.angle(complex(UPN[0][0],UPN[0][1]), deg=True))+";deg"})
            eleList.append({"AU2" :  self.formatAngle(np.angle(complex(UPN[1][0],UPN[1][1]), deg=True))+";deg"})
            eleList.append({"AU3" :  self.formatAngle(np.angle(complex(UPN[2][0],UPN[2][1]), deg=True))+";deg"})

            eleList.append({"AI1" :  self.formatAngle(np.angle(complex(IL[0][0],IL[0][1]), deg=True))+";deg"})
            eleList.append({"AI2" :  self.formatAngle(np.angle(complex(IL[1][0],IL[1][1]), deg=True))+";deg"})
            eleList.append({"AI3" :  self.formatAngle(np.angle(complex(IL[2][0],IL[2][1]), deg=True))+";deg"})
            eleList.append(self.UIPhaseAngleValues(compList))


            Pmode=zeracom.readSafe(vals,["POWER1Module1","PAR_MeasuringMode"])
            SP=zeracom.readSafe(vals,["POWER1Module1","ACT_PQS4"])
            pPowerRowValues=[zeracom.readSafe(vals,["POWER1Module1","ACT_PQS1"]),
                            zeracom.readSafe(vals,["POWER1Module1","ACT_PQS2"]),
                            zeracom.readSafe(vals,["POWER1Module1","ACT_PQS3"]),
                            SP]
            self.computeScaling(pPowerRowValues, scaleInfo)
            pPowerUnit = scaleInfo["unitPrefix"] + "W"
            pPowerUnitWithMode = pPowerUnit + " ("+Pmode+")"
            eleList.append({"P1" :  self.formatNumber(pPowerRowValues[0]*scaleInfo["factor"])+";" + pPowerUnitWithMode})
            eleList.append({"P2" :  self.formatNumber(pPowerRowValues[1]*scaleInfo["factor"])+";" + pPowerUnitWithMode})
            eleList.append({"P3" :  self.formatNumber(pPowerRowValues[2]*scaleInfo["factor"])+";" + pPowerUnitWithMode})
            eleList.append({"SP" :  self.formatNumber(pPowerRowValues[3]*scaleInfo["factor"])+";" + pPowerUnit})

            Qmode=zeracom.readSafe(vals,["POWER1Module2","PAR_MeasuringMode"])
            SQ=zeracom.readSafe(vals,["POWER1Module2","ACT_PQS4"])
            qPowerRowValues=[zeracom.readSafe(vals,["POWER1Module2","ACT_PQS1"]),
                            zeracom.readSafe(vals,["POWER1Module2","ACT_PQS2"]),
                            zeracom.readSafe(vals,["POWER1Module2","ACT_PQS3"]),
                            SQ]
            self.computeScaling(qPowerRowValues, scaleInfo)
            qPowerUnit = scaleInfo["unitPrefix"] + "VAR"
            qPowerUnitWithMode = qPowerUnit + " ("+Qmode+")"
            eleList.append({"Q1" :  self.formatNumber(qPowerRowValues[0]*scaleInfo["factor"])+";" + qPowerUnitWithMode})
            eleList.append({"Q2" :  self.formatNumber(qPowerRowValues[1]*scaleInfo["factor"])+";" + qPowerUnitWithMode})
            eleList.append({"Q3" :  self.formatNumber(qPowerRowValues[2]*scaleInfo["factor"])+";" + qPowerUnitWithMode})
            eleList.append({"SQ" :  self.formatNumber(qPowerRowValues[3]*scaleInfo["factor"])+";" + qPowerUnit})

            Smode=zeracom.readSafe(vals,["POWER1Module3","PAR_MeasuringMode"])
            SS=zeracom.readSafe(vals,["POWER1Module3","ACT_PQS4"])
            sPowerRowValues=[zeracom.readSafe(vals,["POWER1Module3","ACT_PQS1"]),
                            zeracom.readSafe(vals,["POWER1Module3","ACT_PQS2"]),
                            zeracom.readSafe(vals,["POWER1Module3","ACT_PQS3"]),
                            SS]
            self.computeScaling(sPowerRowValues, scaleInfo)
            sPowerUnit = scaleInfo["unitPrefix"] + "VA"
            sPowerUnitWithMode = sPowerUnit + " ("+Smode+")"
            eleList.append({"S1" :  self.formatNumber(sPowerRowValues[0]*scaleInfo["factor"])+";" + sPowerUnitWithMode})
            eleList.append({"S2" :  self.formatNumber(sPowerRowValues[1]*scaleInfo["factor"])+";" + sPowerUnitWithMode})
            eleList.append({"S3" :  self.formatNumber(sPowerRowValues[2]*scaleInfo["factor"])+";" + sPowerUnitWithMode})
            eleList.append({"SS" :  self.formatNumber(sPowerRowValues[3]*scaleInfo["factor"])+";" + sPowerUnit})
            eleList.append({"RF" :  self.formatNumber(str(zeracom.readSafe(vals,["DFTModule1","ACT_RFIELD"])))})
            eleList.append({"FREQ" :  self.formatNumber(zeracom.readSafe(vals,["RangeModule1","ACT_Frequency"]))})

        else: # EMOB DC has power on PowerModule 4
            Pmode=zeracom.readSafe(vals,["POWER1Module4","PAR_MeasuringMode"])
            SP=zeracom.readSafe(vals,["POWER1Module4","ACT_PQS4"])
            pPowerRowValues=[zeracom.readSafe(vals,["POWER1Module4","ACT_PQS1"]),
                            zeracom.readSafe(vals,["POWER1Module4","ACT_PQS2"]),
                            zeracom.readSafe(vals,["POWER1Module4","ACT_PQS3"]),
                            SP]
            self.computeScaling(pPowerRowValues, scaleInfo)
            pPowerUnitWithMode = scaleInfo["unitPrefix"] + "W ("+Pmode+")"
            eleList.append({"P1" :  self.formatNumber(pPowerRowValues[0]*scaleInfo["factor"])+";" + pPowerUnitWithMode})
            eleList.append({"P2" :  self.formatNumber(pPowerRowValues[1]*scaleInfo["factor"])+";" + pPowerUnitWithMode})
            eleList.append({"P3" :  self.formatNumber(pPowerRowValues[2]*scaleInfo["factor"])+";" + pPowerUnitWithMode})
            eleList.append({"RF" : ""})



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

    def LambdaCommon(self,compList, metadata):
        #pylint: disable=unused-argument
        vals=zeracom.entityComponentSort(compList["values"])
        eleList=[]

        if not self.IsEmobDcSession(vals):
            eleList.append({"Lambda1" :  self.formatNumber(zeracom.readSafe(vals,["LambdaModule1","ACT_Lambda1"]))})
            eleList.append({"Lambda2" :  self.formatNumber(zeracom.readSafe(vals,["LambdaModule1","ACT_Lambda2"]))})
            eleList.append({"Lambda3" :  self.formatNumber(zeracom.readSafe(vals,["LambdaModule1","ACT_Lambda3"]))})
            eleList.append({"SLambda" :  self.formatNumber(zeracom.readSafe(vals,["LambdaModule1","ACT_Lambda4"]))})

        return eleList

    def convertZeraGuiActualValues(self,compList, metadata):
        endResult=[]
        result={}
        eleList=[]
        eleList.append({"Datatype" : "Actual-Values"})
        eleList.append({"Function" : "Value-Measurement"})

        eleList.append(self.TimeCommon("AV ",compList))
        eleList.append(self.ActualValuesCommon(compList,metadata, vectorMeasurement = False))
        eleList.append(self.LambdaCommon(compList,metadata))

        result["#childs"]=eleList
        endResult.append(result)
        return endResult

    def convertZeraGuiVectorDiagramm(self,compList, metadata):
        endResult=[]
        result={}
        eleList=[]
        eleList.append(self.TimeCommon("VV ",compList))
        eleList.append({"Datatype" : "Actual-Values"})
        eleList.append({"Function" : "Vector-Measurement"})
        eleList.append(self.ActualValuesCommon(compList,metadata, vectorMeasurement = True))
        eleList.append(self.LambdaCommon(compList,metadata))

        result["#childs"]=eleList
        endResult.append(result)
        return endResult

    def convertZeraGuiPowerValues(self,compList, metadata):
        return self.convertZeraGuiActualValues(compList,metadata)

    def convertZeraGuiRMSValues(self,compList, metadata):
        return self.convertZeraGuiActualValues(compList,metadata)

    def convertZeraGuiHarmonicTable(self,compList, metadata):
        vals=zeracom.entityComponentSort(compList["values"])
        endresult=[]
        result={}
        eleList=[]
        channelMap={}
        channelMap["1"]=["U1","V"]
        channelMap["2"]=["U2","V"]
        channelMap["3"]=["U3","V"]
        channelMap["4"]=["I1","A"]
        channelMap["5"]=["I2","A"]
        channelMap["6"]=["I3","A"]
        channelMap["7"]=["UAUX","V"]
        channelMap["8"]=["IAUX","A"]

        upper=7
        if "ACT_FFT7" in vals["FFTModule1"]:
            upper=9

        for ch in range(1,upper):
            result={}
            eleList=[]
            eleList.append(self.SessionDeviceInfo(metadata, 'DEU'))

            eleList.append({"Function" : "Harmonics-Measurement"})
            eleList.append({"Datatype" : "Harmonic-Data"})
            NameAdd=""
            unit=""

            NameAdd=channelMap[str(ch)][0]
            unit=channelMap[str(ch)][1]
            eleList.append(self.TimeCommon("HT "+NameAdd+" ",compList))

            eleList.append(self.RangeCommon(compList))

            eleList.append(self.ScaleCommon(compList, metadata))
            eleList.append({"M-Mode" : ""})
            eleList.append({"Channel" : NameAdd})

            if zeracom.readSafe(vals,["THDNModule1","ACT_THDN"+ str(ch)]) is not None:
                eleList.append({"Total-Harm" :  self.formatNumber(zeracom.readSafe(vals,["THDNModule1","ACT_THDN"+ str(ch)]))+";%"})

            count = 0
            i=0
            real = zeracom.readSafe(vals,["FFTModule1","ACT_FFT"+ str(ch)]).split(";")[2]
            imag = zeracom.readSafe(vals,["FFTModule1","ACT_FFT"+ str(ch)]).split(";")[3]
            baseAbs = np.linalg.norm(np.array([float(real),float(imag)]))
            baseAng = np.angle(complex(float(real),float(imag)), deg=True)
            for sample in zeracom.readSafe(vals,["FFTModule1","ACT_FFT"+ str(ch)]).split(";"):
                count = count + 1
                if count >= 2:
                    count = 0
                    imag = sample
                    val = np.array([float(real),float(imag)])
                    if i != 1:
                        eleList.append({"Harm" :  str(i)+";"+ self.formatNumber(np.linalg.norm(val)/baseAbs*100)+";%;"+ self.formatAngle(np.angle(complex(val[0],val[1]), deg=True))+";deg"})
                    else:
                        eleList.append({"Harm" :  str(i)+";"+self.formatNumber(baseAbs)+";"+unit+";"+self.formatNumber(baseAng)+";deg"})

                    i=i+1
                else:
                    real = sample

            result["#childs"]=eleList
            endresult.append(result)

        return endresult

    def convertZeraGuiHarmonicChart(self,compList,metadata):
        return self.convertZeraGuiHarmonicTable(compList,metadata)

    def convertZeraGuiCurveDisplay(self,compList,metadata):
        vals=zeracom.entityComponentSort(compList["values"])
        result={}
        endResult=[]
        eleList=[]
        endResult.append(result)

        phases = [[1, 4], [2, 5], [3, 6], [7, 8]]
        for phase in range(len(phases)):
            UIdx = phases[phase][0]
            if zeracom.readSafe(vals,["OSCIModule1","ACT_OSCI"+ str(UIdx)]) == "":
                continue
            IIdx = phases[phase][1]
            phaseName = str(phase+1)
            if phase == 3:
                phaseName = "AUX"
            result={}
            eleList=[]
            eleList.append(self.SessionDeviceInfo(metadata, 'DEU'))
            eleList.append({"Function" : "Curve-Measurement"})
            eleList.append({"Datatype" : "Sample-Data"})

            eleList.append(self.TimeCommon("CD " + "UI " + phaseName + " ", compList))

            eleList.append(self.ScaleCommon(compList, metadata))
            eleList.append({"M-Mode" : ""})

            eleList.append(self.RangeCommon(compList, True))

            i=0
            for sample in zeracom.readSafe(vals,["OSCIModule1","ACT_OSCI"+ str(UIdx)]).split(";"):
                i=i+1
                eleList.append({"SampleA" :  self.formatNumber(i)+";"+sample+";V"})

            eleList.append({"ChannelA" : "U" + phaseName})

            i=0
            for sample in zeracom.readSafe(vals,["OSCIModule1","ACT_OSCI"+ str(IIdx)]).split(";"):
                i=i+1
                eleList.append({"SampleB" :  self.formatNumber(i)+";"+sample+";A"})

            eleList.append({"ChannelB" : "I" + phaseName})

            result["#childs"]=eleList
            endResult.append(result)

        return endResult

    def convertZeraGuiHarmonicPowerTable(self,compList,metadata):
        vals=zeracom.entityComponentSort(compList["values"])
        result={}
        endResult=[]
        eleList=[]

        phaseCount = 3
        for phase in range(1, phaseCount+1):
            uIdx = phase
            iIdx = phase + phaseCount
            phaseStr = str(phase)
            result={}
            eleList=[]
            eleList.append(self.SessionDeviceInfo(metadata, 'DEU'))

            eleList.append({"Function" : "Selektiv-Measurement"})
            eleList.append({"Datatype" : "Selektiv-Data"})

            eleList.append(self.TimeCommon("HP "+ "UI" + phaseStr + " ", compList))

            eleList.append(self.ScaleCommon(compList, metadata))
            eleList.append({"M-Mode" : ""})

            eleList.append(self.RangeCommon(compList))

            eleList.append({"ChannelU" : "U" + phaseStr})
            eleList.append({"ChannelI" : "I" + phaseStr})

            uFftTotal = zeracom.readSafe(vals,["FFTModule1","ACT_FFT" + str(uIdx)])
            iFftTotal = zeracom.readSafe(vals,["FFTModule1","ACT_FFT" + str(iIdx)])
            fftLen = len(zeracom.readSafe(vals,["FFTModule1","ACT_FFT" + phaseStr]).split(";"))
            for i in range(0, int(fftLen/2)):
                uRe = float(uFftTotal.split(";")[2*i])
                uIm = float(uFftTotal.split(";")[2*i+1])
                U = math.sqrt(uRe*uRe + uIm*uIm)
                iRe = float(iFftTotal.split(";")[2*i])
                iIm = float(iFftTotal.split(";")[2*i+1])
                I = math.sqrt(iRe*iRe + iIm*iIm)

                P = float(zeracom.readSafe(vals,["Power3Module1","ACT_HPP"+ phaseStr]).split(";")[i])
                Q = float(zeracom.readSafe(vals,["Power3Module1","ACT_HPQ"+ phaseStr]).split(";")[i])
                S = float(zeracom.readSafe(vals,["Power3Module1","ACT_HPS"+ phaseStr]).split(";")[i])
                eleList.append({"HarmValue" : "N;" + str(i)+";U;"+ self.formatNumber(U)+";V;I;"+ self.formatNumber(I)+";A;P;"+ self.formatNumber(P)+";W;Q;"+ self.formatNumber(Q)+";var;S;"+ self.formatNumber(S)+";VA"})

            result["#childs"] = eleList
            endResult.append(result)

        return endResult

    def convertZeraGuiHarmonicPowerChart(self,compList,metadata):
        return self.convertZeraGuiHarmonicPowerTable(compList,metadata)

    def convertZeraGuiMeterTest(self,compList,metadata):
        vals=zeracom.entityComponentSort(compList["values"])
        result={}
        eleList=[]

        eleList=self.ActualValuesCommon(compList, metadata, vectorMeasurement = False)
        eleList.append(self.LambdaCommon(compList,metadata))
        eleList.append(self.TimeCommon("MT ",compList))

        eleList.append({"Device-No" : metadata["device"]["serial"]})

        eleList.append({"AdjustData" : ""})
        eleList.append({"Function" : "Error-Measurement"})
        eleList.append({"Datatype" : "Meter-Error"})
        eleList.append({"Place-No" : "1"})

        mode=""
        if  self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","PAR_RefInput"])) == "P":
            mode=zeracom.readSafe(vals,["POWER1Module1","PAR_MeasuringMode"])
        elif  self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","PAR_RefInput"])) == "Q":
            mode=zeracom.readSafe(vals,["POWER1Module2","PAR_MeasuringMode"])
        elif  self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","PAR_RefInput"])) == "S":
            mode=zeracom.readSafe(vals,["POWER1Module3","PAR_MeasuringMode"])
        elif  self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","PAR_RefInput"])) == "P AC":
            mode=zeracom.readSafe(vals,["POWER1Module1","PAR_MeasuringMode"])
        elif  self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","PAR_RefInput"])) == "P DC":
            mode=zeracom.readSafe(vals,["POWER1Module4","PAR_MeasuringMode"])
        eleList.append({"M-Mode" :  self.formatNumber(mode)})

        # eleList.append({"RF" : ""})
        eleList.append({"Cz" :  self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","PAR_DutConstant"]))+";"+"x1"+";"+ self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","PAR_DUTConstUnit"]))})
        eleList.append({"M-Puls" :  str(zeracom.readSafe(vals,["SEC1Module1","PAR_MRate"]))})
        eleList.append({"M-Inp" : self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","PAR_DutInput"]))})
        eleList.append({"Error" :  self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","ACT_Result"]))+"%"})

        eleList.append({"StartTime" :  self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","ACT_StartTime"]))})
        eleList.append({"StopTime" :  self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","ACT_EndTime"]))})
        durationMs = zeracom.readSafe(vals, ["SEC1Module1","ACT_MeasTime"])
        eleList.append({"MTime" : self.ms_to_hh_mm_ss(durationMs)})

        eleList.append({"Err-Energie" :  self.formatNumber(zeracom.readSafe(vals,["SEC1Module1","ACT_Energy"]))+";kWh"})

        multiMeasJson=zeracom.readSafe(vals,["SEC1Module1","ACT_MulResult"])
        totalCount=0
        try:
            multimeas=json.loads(multiMeasJson)
            totalCount = zeracom.readSafe(vals,["SEC1Module1","ACT_MulCount"])
        except:
            totalCount=0
        # maybe we should think about a totalCount in ACT_MulResult...

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

    def convertZeraGuiEnergyComparison(self,compList, metadata):
        #pylint: disable=unused-argument
        print("MtVis can not display Energy Comparison Data")

    def convertZeraGuiEnergyRegister(self,compList,metadata):
        vals=zeracom.entityComponentSort(compList["values"])
        result={}
        eleList=[]
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : ""})
        eleList.append({"Device-Typ" : metadata["device"]["type"]})
        eleList.append({"Device-No" : metadata["device"]["serial"]})

        eleList.append({"AdjustData" : "ok"})
        datetimeObj= datetime.strptime(compList["timestemp"], '%a %b %d %H:%M:%S %Y')

        eleList.append(self.TimeCommon("ER ",compList))

        eleList.append(self.RangeCommon(compList))

        mode=""
        if  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","PAR_RefInput"])) == "P":
            mode=zeracom.readSafe(vals,["POWER1Module1","PAR_MeasuringMode"])
        elif  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","PAR_RefInput"])) == "Q":
            mode=zeracom.readSafe(vals,["POWER1Module2","PAR_MeasuringMode"])
        elif  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","PAR_RefInput"])) == "S":
            mode=zeracom.readSafe(vals,["POWER1Module3","PAR_MeasuringMode"])
        eleList.append({"M-Mode" :  self.formatNumber(mode)})
        eleList.append(self.ScaleCommon(compList, metadata))
        eleList.append({"Function" : "Register-Test"})
        eleList.append({"Datatype" : "Register-Test"})
        eleList.append({"Place-No" : "1"})
        if zeracom.readSafe(vals,["SEM1Module1","PAR_Targeted"]) == 1:
            eleList.append({"Type" : "Duration"})

        else:
            eleList.append({"Type" : "Start/Stop"})

        if zeracom.readSafe(vals,["SEM1Module1","ACT_StartTime"]) != "": # introduced in 4.7.3
            eleList.append({"E-StartTime" :  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","ACT_StartTime"]))})
            eleList.append({"E-StopTime" :  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","ACT_EndTime"]))})
            durationMs = zeracom.readSafe(vals, ["SEM1Module1","ACT_MeasTime"])
            eleList.append({"E-MTime" : self.ms_to_hh_mm_ss(durationMs)})
        else:
            eleList.append({"E-MTime" :  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","ACT_Time"]))+" s"})

        eleList.append({"Energie" :  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","ACT_Energy"]))+";"+ self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","PAR_TXUNIT"]))})          # wird benötigt
        eleList.append({"E-Begin" :  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","PAR_T0Input"]))+";"+ self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","PAR_TXUNIT"]))})    # wird benötigt
        eleList.append({"E-End" :  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","PAR_T1input"]))+";"+ self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","PAR_TXUNIT"]))})      # wird benötigt
        eleList.append({"E-Cz" :  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","PAR_TXUNIT"]))})       # wird benötigt
        eleList.append({"E-Error" :  self.formatNumber(zeracom.readSafe(vals,["SEM1Module1","ACT_Result"]))+";%"})    # wird benötigt

        result["#childs"]=eleList
        return result

    def convertZeraGuiPowerRegister(self,compList, metadata):
        vals=zeracom.entityComponentSort(compList["values"])
        result={}
        eleList=[]
        eleList.append(self.SessionDeviceInfo(metadata, ''))
        eleList.append({"AdjustData" : ""})

        eleList.append(self.TimeCommon("PR ",compList))

        eleList.append(self.RangeCommon(compList))

        mode = ""
        if  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","PAR_RefInput"])) == "P":
            mode=zeracom.readSafe(vals,["POWER1Module1","PAR_MeasuringMode"])
        elif  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","PAR_RefInput"])) == "Q":
            mode=zeracom.readSafe(vals,["POWER1Module2","PAR_MeasuringMode"])
        elif  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","PAR_RefInput"])) == "S":
            mode=zeracom.readSafe(vals,["POWER1Module3","PAR_MeasuringMode"])
        eleList.append({"M-Mode" :  self.formatNumber(mode)})
        eleList.append(self.ScaleCommon(compList, metadata))
        eleList.append({"Function" : "Register-Test"})
        eleList.append({"Datatype" : "Register-Test"})
        eleList.append({"Place-No" : "1"})
        if zeracom.readSafe(vals,["SPM1Module1","PAR_Targeted"]) == 1:
            eleList.append({"Type" : "Duration"})

        else:
            eleList.append({"Type" : "Start/Stop"})

        if zeracom.readSafe(vals,["SPM1Module1","ACT_StartTime"]) != "": # introduced in 4.7.3
            eleList.append({"P-StartTime" :  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","ACT_StartTime"]))})
            eleList.append({"P-StopTime" :  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","ACT_EndTime"]))})
            durationMs = zeracom.readSafe(vals, ["SPM1Module1","ACT_MeasTime"])
            eleList.append({"P-MTime" : self.ms_to_hh_mm_ss(durationMs)})
        else:
            eleList.append({"P-MTime" :  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","ACT_Time"]))+" s"})


        eleList.append({"Power" :  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","ACT_Power"]))+";"+ self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","PAR_TXUNIT"]))})          # wird benötigt
        eleList.append({"P-Begin" :  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","PAR_T0Input"]))+";"+ self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","PAR_TXUNIT"]))})    # wird benötigt
        eleList.append({"P-End" :  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","PAR_T1input"]))+";"+ self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","PAR_TXUNIT"]))})      # wird benötigt
        eleList.append({"P-Cz" :  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","PAR_TXUNIT"]))})       # wird benötigt
        eleList.append({"P-Error" :  self.formatNumber(zeracom.readSafe(vals,["SPM1Module1","ACT_Result"]))+";%"})    # wird benötigt

        result["#childs"]=eleList
        return result

    def convertZeraGuiVoltageBurden(self,compList, metadata):
        vals=zeracom.entityComponentSort(compList["values"])
        result={}
        eleList=[]

        eleList=self.SessionDeviceInfo(metadata, 'DEU')
        eleList.append(self.ScaleCommon(compList, metadata))
        eleList.append(self.RangeCommon(compList))
        eleList.append(self.UPNRmsValues(compList, vectorMeasurement = False))
        eleList.append(self.IValues(compList, vectorMeasurement = False))
        eleList.append(self.UIPhaseAngleValues(compList))
        eleList.append(self.TimeCommon("VB ",compList))
        eleList.append({"M-Mode" : ""})
        eleList.append({"Function" : "U-Burden"})
        eleList.append({"Datatype" : "UBurden-Value"})
        eleList.append(self.VoltageBurdenValues(compList))
        eleList.append({"U-Nominal" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","PAR_NominalRange"]))+";V"})
        eleList.append({"B-Nominal" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","PAR_NominalBurden"]))+";VA"})
        eleList.append({"W-Length" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","PAR_WireLength"]))+";m"})
        eleList.append({"W-Gauge" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module2","PAR_WCrosssection"]))+";mm2"})

        result["#childs"]=eleList
        return result

    def convertZeraGuiCurrentBurden(self,compList, metadata):
        vals=zeracom.entityComponentSort(compList["values"])
        result={}
        eleList=[]

        eleList=self.SessionDeviceInfo(metadata, 'DEU')
        eleList.append(self.ScaleCommon(compList, metadata))
        eleList.append(self.RangeCommon(compList))
        eleList.append(self.UPNRmsValues(compList, vectorMeasurement = False))
        eleList.append(self.IValues(compList, vectorMeasurement = False))
        eleList.append(self.UIPhaseAngleValues(compList))
        eleList.append(self.TimeCommon("CB ",compList))
        eleList.append({"M-Mode" : ""})
        eleList.append({"Function" : "I-Burden"})
        eleList.append({"Datatype" : "IBurden-Value"})
        eleList.append(self.CurrentBurdenValues(compList))
        eleList.append({"I-Nominal" :  self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","PAR_NominalRange"]))+";A"})
        eleList.append({"B-Nominal" :   self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","PAR_NominalBurden"]))+";VA"})
        eleList.append({"W-Length" :   self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","PAR_WireLength"]))+";m"})
        eleList.append({"W-Gauge" :   self.formatNumber(zeracom.readSafe(vals,["Burden1Module1","PAR_WCrosssection"]))+";mm2"})

        result["#childs"]=eleList
        return result

    def convertZeraGuiInstrumentTransformer(self,compList, metadata):
        vals=zeracom.entityComponentSort(compList["values"])
        result={}
        eleList=[]
        eleList.append(self.SessionDeviceInfo(metadata, 'DEU'))
        eleList.append({"AdjustData" : ""})

        eleList.append(self.TimeCommon("IT ",compList))

        eleList.append(self.RangeCommon(compList))

        eleList.append({"M-Mode" : ""})
        eleList.append(self.ScaleCommon(compList, metadata))
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
        eleList.append({"CT-N" :  self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","PAR_PrimClampPrim"]))+"/"+ self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","PAR_PrimClampSec"]))+";A"})
        eleList.append({"CT-X" :  self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","PAR_DutPrimary"]))+"/"+ self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","PAR_DutSecondary"]))+";A"})
        eleList.append({"CT_Xc" :  self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","PAR_SecClampPrim"]))+"/"+ self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","PAR_SecClampSec"]))+"/"+ self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","PAR_DutSecondary"]))+";A"})
        eleList.append({"I-Prim" :  self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","ACT_IXPrimary1"]))+";A"})     # wird benötigt
        eleList.append({"I-Sek-N" :  self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","ACT_INSecondary1"]))+";A"})     # wird benötigt
        eleList.append({"I-Sek-X" :  self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","ACT_IXSecondary1"]))+";A"})     # wird benötigt
        #@TODO XC is missing
        eleList.append({"CT-Value" :  self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","ACT_Error1"]))+";%"})
        eleList.append({"CT-Angle-deg" :  self.formatNumber(zeracom.readSafe(vals,["Transformer1Module1","ACT_Angle1"]))+";deg"})
        acrad=zeracom.readSafe(vals,["Transformer1Module1","ACT_Angle1"])*math.pi/180*100
        amin=zeracom.readSafe(vals,["Transformer1Module1","ACT_Angle1"])*60
        eleList.append({"CT-Angle-min" :  self.formatNumber(amin)+";min"})
        eleList.append({"CT-Angle-crad" :  self.formatNumber(acrad)+";crad"})
        # eleList.append({"VTCT-Value" : ""})
        # eleList.append({"VTCT-Angle-deg" : ""})
        # eleList.append({"VTCT-Angle-min" : ""})
        # eleList.append({"VTCT-Angle-crad" : ""})

        result["#childs"]=eleList
        return result

    def convertZeraGuiCEDPower(self,compList, metadata):
        #pylint: disable=unused-argument
        print("MtVis can not display CED Power Data")

    def convertZeraGuiDCReference(self,compList, metadata):
        #pylint: disable=unused-argument
        print("MtVis can not Display DC Reference Data")

    def convertZeraAll(self,compList, metadata):
        endResult=[]
        funcList=[]
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
                ret=func(compList,metadata)
                if type(ret) is list:
                    for ele in ret:
                        res={}
                        res=ele
                        endResult.append(res)
                elif type(ret) is dict:
                    res={}
                    res=ret
                    endResult.append(res)
            except BaseException as err:
                logging.warning("Converting transaction failed with: "+str(err))
                res={}

        return endResult

