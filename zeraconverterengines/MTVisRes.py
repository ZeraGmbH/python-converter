
from datetime import datetime
import math
import numpy as np

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

        print(self.__convertDict)


    def testFunc(self):
        print("Mapped function called")


    def setInput(self, p_dict):
        self.__inputDict=p_dict

    def getOutput(self):
        return self.__outputDict

    def setParams(self,params):
        try:
            if "digits" in params:
                self.__digits=int(params["digits"])
            if "decimalPlaces" in params:
                self.__dec=int(params["decimalPlaces"])
            if "local" in params:
                self.__local=params["local"]
        except:
            return

    def manipulate(self):
        print("Manipulate")
        self.__outputDict["result-Data"]={"#childs" : []}
        self.iterateTransactions()

    def iterateTransactions(self):
        for session in self.__inputDict.keys(): 
            for key in self.__inputDict[session]["dynamic"].keys(): 
                contentSets=self.__inputDict[session]["dynamic"][key]["contentset_names"].split(",")     
                guiContext=self.__inputDict[session]["dynamic"][key]["guiContext"]
          
                for content in self.__convertDict.keys():
                    if content in contentSets:
                        for guiCon in self.__convertDict[content].keys():
                            if guiCon == guiContext or content == "ZeraAll":
                                if content == "ZeraAll": 
                                    resList=self.__convertDict[content]["ZeraAll"](self.__inputDict[session]["dynamic"][key],{"session" : session, "transaction" : key})
                                else:
                                    resList=self.__convertDict[content][guiCon](self.__inputDict[session]["dynamic"][key],{"session" : session, "transaction" : key})

                                if type(resList) is list:
                                    for ele in resList:
                                        res=dict()
                                        res["Result"]=ele
                                        self.__outputDict["result-Data"]["#childs"].append(res)
                                elif type(resList) is dict:
                                    res=dict()
                                    res["Result"]=resList
                                    self.__outputDict["result-Data"]["#childs"].append(res)
                        
        

    def entityComponentSort(self,input):
        result=dict()
        for ele in input:
            compDict=dict()
            if ele["entity_name"] in result:
                compDict=result[ele["entity_name"]]
            compDict[ele["component_name"]] = ele["component_value"]
            result[ele["entity_name"]]=compDict
        return result

    
    def ActualValuesGeneric(self,input, metadata):
        vals=self.entityComponentSort(input["values"])
        eleList=list()
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : "DEU"})
        eleList.append({"Device-Typ" : "MT310s2"})
        eleList.append({"Device-No" : "MT310s2"})
        datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')
        time=datetimeObj.strftime("%H/%M/%S")
        date=datetimeObj.strftime("%d/%m/%Y")
        eleList.append({"Time" : time})
        eleList.append({"Date" : date})
       

        eleList.append({"U-PrimSek" : "1"})
        eleList.append({"I-PrimSek" : "1"})
        eleList.append({"M-Mode" : ""})
        eleList.append({"PrimSek-Val-Cz-Reg" : ""})

        URange=float(0)
        IRange=float(0)
        for ch in range(1,4):    
            if URange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                URange=float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1])
            if URange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                IRange=float(vals["RangeModule1"]["PAR_Channel"+str(ch+4)+"Range"][:-1])

        eleList.append({"U-Range" : str(URange)+";V"})
        eleList.append({"I-Range" : str(IRange)+";A"})
        
        UPN=list()

        UPN.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN1"].split(";")]))
        UPN.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN2"].split(";")]))
        UPN.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN3"].split(";")]))

        eleList.append({"UPN1" : str(round(np.linalg.norm(UPN[0]),4))+";V"})
        eleList.append({"UPN2" : str(round(np.linalg.norm(UPN[1]),4))+";V"})
        eleList.append({"UPN3" : str(round(np.linalg.norm(UPN[2]),4))+";V"})

        eleList.append({"UPP12" : str(round(np.linalg.norm(UPN[0]+UPN[1]),4))+";V"})
        eleList.append({"UPP23" : str(round(np.linalg.norm(UPN[1]+UPN[2]),4))+";V"})
        eleList.append({"UPP31" : str(round(np.linalg.norm(UPN[2]+UPN[0]),4))+";V"})

        IL=list()

        IL.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN4"].split(";")]))
        IL.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN5"].split(";")]))
        IL.append(np.array([float(i) for i in vals["DFTModule1"]["ACT_DFTPN6"].split(";")]))

        eleList.append({"IL1" : str(round(np.linalg.norm(IL[0]),4))+";A"})
        eleList.append({"IL2" : str(round(np.linalg.norm(IL[1]),4))+";A"})
        eleList.append({"IL3" : str(round(np.linalg.norm(IL[2]),4))+";A"})

        eleList.append({"IDC1" : ""})
        eleList.append({"IDC2" : ""})
        eleList.append({"IDC3" : ""})

        eleList.append({"AU1" : str(round(np.angle(np.complex(UPN[0][0],UPN[0][1]), deg=True),4))+";deg"})
        eleList.append({"AU2" : str(round(np.angle(np.complex(UPN[1][0],UPN[1][1]), deg=True),4))+";deg"})
        eleList.append({"AU3" : str(round(np.angle(np.complex(UPN[2][0],UPN[2][1]), deg=True),4))+";deg"})

        eleList.append({"AI1" : str(round(np.angle(np.complex(IL[0][0],IL[0][1]), deg=True),4))+";deg"})
        eleList.append({"AI2" : str(round(np.angle(np.complex(IL[1][0],IL[1][1]), deg=True),4))+";deg"})
        eleList.append({"AI3" : str(round(np.angle(np.complex(IL[2][0],IL[2][1]), deg=True),4))+";deg"})

        eleList.append({"PHI1" : ""})
        eleList.append({"PHI2" : ""})
        eleList.append({"PHI3" : ""})
        '''
        eleList.append({"S1" :  str(vals["POWER1Module3"]["ACT_PQS1"])+";VA"})
        eleList.append({"S2" :  str(vals["POWER1Module3"]["ACT_PQS3"])+";VA"})
        eleList.append({"S3" :  str(vals["POWER1Module3"]["ACT_PQS3"])+";VA"})
        
        eleList.append({"P1" : str(vals["POWER1Module1"]["ACT_PQS1"])+";W"})
        eleList.append({"P2" : str(vals["POWER1Module1"]["ACT_PQS2"])+";W"})
        eleList.append({"P3" : str(vals["POWER1Module1"]["ACT_PQS3"])+";W"})

        eleList.append({"Q1" : str(vals["POWER1Module2"]["ACT_PQS1"])+";VAR"})
        eleList.append({"Q2" : str(vals["POWER1Module2"]["ACT_PQS2"])+";VAR"})
        eleList.append({"Q3" : str(vals["POWER1Module2"]["ACT_PQS3"])+";VAR"})

        
        SP=vals["POWER1Module1"]["ACT_PQS1"]+vals["POWER1Module1"]["ACT_PQS2"]+vals["POWER1Module1"]["ACT_PQS3"]
        SQ=vals["POWER1Module2"]["ACT_PQS1"]+vals["POWER1Module2"]["ACT_PQS2"]+vals["POWER1Module2"]["ACT_PQS3"]
        SS=vals["POWER1Module3"]["ACT_PQS1"]+vals["POWER1Module3"]["ACT_PQS2"]+vals["POWER1Module3"]["ACT_PQS3"]

        eleList.append({"SS" : str(SS)+";VA"})
        eleList.append({"SP" : str(SP)+";W"})
        eleList.append({"SQ" : str(SQ)+";var"})
        '''
        eleList.append({"RF" : ""})
        eleList.append({"FREQ" : str(round(vals["RangeModule1"]["ACT_Frequency"],4))})
        eleList.append({"UD1" : ""})
        eleList.append({"UD2" : ""})
        eleList.append({"UD3" : ""})
        eleList.append({"ID1" : ""})
        eleList.append({"ID2" : ""})
        eleList.append({"ID3" : ""})
        
        '''
        eleList.append({"Lambda1" : vals["LambdaModule1"]["ACT_Lambda1"]})
        eleList.append({"Lambda2" : vals["LambdaModule1"]["ACT_Lambda2"]})
        eleList.append({"Lambda3" : vals["LambdaModule1"]["ACT_Lambda3"]})
        ''' 

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


    def convertZeraGuiActualValues(self,input, metadata):
        endResult=list()
        result=dict()
        eleList=list()
        eleList.append({"Datatype" : "Actual-Values"})
        eleList.append({"Function" : "Value-Measurement"})
        eleList.append(self.ActualValuesGeneric(input,metadata))
        
        result["#childs"]=eleList
        endResult.append(result)
        return endResult



    def convertZeraGuiVectorDiagramm(self,input, metadata):
        endResult=list()
        result=dict()
        eleList=list()
        eleList.append({"Datatype" : "Actual-Values"})
        eleList.append({"Function" : "Vector-Measurement"})
        eleList.append(self.ActualValuesGeneric(input,metadata))
        
        
        result["#childs"]=eleList
        endResult.append(result)
        return endResult

    def convertZeraGuiPowerValues(self,input, metadata):
        return self.convertZeraGuiActualValues(input,metadata)

    def convertZeraGuiRMSValues(self,input, metadata):
        return self.convertZeraGuiActualValues(input,metadata)

    def convertZeraGuiHarmonicTable(self,input, metadata):
        vals=self.entityComponentSort(input["values"])
        endresult=list()
        result=dict()
        eleList=list()

        for ch in range(1,9):
            result=dict()
            eleList=list()
            eleList.append({"ID" : metadata["session"]})
            eleList.append({"Language" : "DEU"})
            eleList.append({"Device-Typ" : "MT310s2"})
            eleList.append({"Device-No" : "MT310s2"})
            eleList.append({"Function" : "Harmonics-Measurement"})
            eleList.append({"Datatype" : "Harmonic-Data"})
            datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')
            time=datetimeObj.strftime("%H/%M/%S")
            date=datetimeObj.strftime("%d/%m/%Y")
            eleList.append({"Time" : time})
            NameAdd=str()

            if ch < 5:
                NameAdd=" U"+str(ch)
            else:
                NameAdd=" I"+str(ch-4)

            eleList.append({"Date" : NameAdd+" "+date})

            URange=float(0)
            IRange=float(0)
            for c in range(1,4):    
                if URange < float(vals["RangeModule1"]["PAR_Channel"+str(c)+"Range"][:-1]):
                    URange=float(vals["RangeModule1"]["PAR_Channel"+str(c)+"Range"][:-1])
                if IRange < float(vals["RangeModule1"]["PAR_Channel"+str(c)+"Range"][:-1]):
                    IRange=float(vals["RangeModule1"]["PAR_Channel"+str(c+4)+"Range"][:-1])

            eleList.append({"U-PrimSek" : "1"})
            eleList.append({"I-PrimSek" : "1"})
            eleList.append({"M-Mode" : ""})
            eleList.append({"PrimSek-Val-Cz-Reg" : ""})

            if ch < 5:
                eleList.append({"Channel" : "UL"+str(ch)})
            else:
                eleList.append({"Channel" : "IL"+str(ch-4)})
            
            eleList.append({"Total-Harm" : str(vals["THDNModule1"]["ACT_THDN"+str(ch)])+";%"})

            count = 0
            i=0
            real = vals["FFTModule1"]["ACT_FFT"+str(ch)].split(";")[2]
            imag = vals["FFTModule1"]["ACT_FFT"+str(ch)].split(";")[3]
            baseAbs = np.linalg.norm(np.array([float(real),float(imag)]))
            baseAng = np.angle(np.array([float(real),float(imag)]))
            for sample in vals["FFTModule1"]["ACT_FFT"+str(ch)].split(";"):
                count = count + 1
                if count >= 2:
                    count = 0
                    imag = sample
                    val = np.array([float(real),float(imag)])
                    eleList.append({"Harm" : str(i)+";"+str(round(np.linalg.norm(val)/baseAbs*100,4))+";%;"+str(round(np.angle(np.complex(val[0],val[1]), deg=True),4))+";deg"})
                    i=i+1
                else:
                    real = sample

            result["#childs"]=eleList
            endresult.append(result)

        return endresult

    def convertZeraGuiHarmonicChart(self,input,metadata):
        return self.convertZeraGuiHarmonicTable(input,metadata)
        
        
        
    def convertZeraGuiCurveDisplay(self,input,metadata):
        vals=self.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        endResult.append(result)
        
        for ch in range(1,5):
            result=dict()
            eleList=list()
            eleList.append({"ID" : metadata["session"]})
            eleList.append({"Language" : "DEU"})
            eleList.append({"Device-Typ" : "MT310s2"})
            eleList.append({"Device-No" : "MT310s2"})
            eleList.append({"Function" : "Curve-Measurement"})
            eleList.append({"Datatype" : "Sample-Data"})
            datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')
            time=datetimeObj.strftime("%H/%M/%S")
            date=datetimeObj.strftime("%d/%m/%Y")
            eleList.append({"Time" : time})
            eleList.append({"Date" : "UI"+str(ch) +" "+date})

            eleList.append({"U-PrimSek" : "1"})
            eleList.append({"I-PrimSek" : "1"})
            eleList.append({"M-Mode" : ""})
            eleList.append({"PrimSek-Val-Cz-Reg" : ""})
            if "-" in vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]:
                eleList.append({"U-Range" : "10;V"})
            else:
                eleList.append({"U-Range" : vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]+";V"})
                
            if "-" in vals["RangeModule1"]["PAR_Channel"+str(ch+4)+"Range"][:-1]:
                eleList.append({"I-Range" : "10;A"})
            else:
                eleList.append({"I-Range" : vals["RangeModule1"]["PAR_Channel"+str(ch+4)+"Range"][:-1]+";A"})

            eleList.append({"ChannelA" : "U"+str(ch)})

            i=0    
            for sample in vals["OSCIModule1"]["ACT_OSCI"+str(ch)].split(";"):
                i=i+1
                eleList.append({"SampleA" : str(i)+";"+sample+";V"})

            eleList.append({"ChannelB" : "I"+str(ch)})

            i=0    
            for sample in vals["OSCIModule1"]["ACT_OSCI"+str(ch+4)].split(";"):
                i=i+1
                eleList.append({"SampleB" : str(i)+";"+sample+";A"})
            result["#childs"]=eleList
            endResult.append(result)
        
        
        return endResult




    def convertZeraGuiHarmonicPowerTable(self,input,metadata):
        vals=self.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        

        for ch in range(1,4):
            result=dict()
            eleList=list()
            eleList.append({"ID" : metadata["session"]})
            eleList.append({"Language" : "DEU"})
            eleList.append({"Device-Typ" : "MT310s2"})
            eleList.append({"Device-No" : "MT310s2"})
            eleList.append({"Function" : "Selektiv-Measurement"})
            eleList.append({"Datatype" : "Selektiv-Data"})
            datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')
            time=datetimeObj.strftime("%H/%M/%S")
            date=datetimeObj.strftime("%d/%m/%Y")
            eleList.append({"Time" : time})
            eleList.append({"Date" : "UI"+str(ch)+" "+date})

            eleList.append({"U-PrimSek" : "1"})
            eleList.append({"I-PrimSek" : "1"})
            eleList.append({"M-Mode" : ""})
            eleList.append({"PrimSek-Val-Cz-Reg" : ""})
            eleList.append({"U-Range" : vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]+";V"})
            eleList.append({"I-Range" : vals["RangeModule1"]["PAR_Channel"+str(ch+4)+"Range"][:-1]+";A"})

            eleList.append({"ChannelU" : "U"+str(ch)})
            eleList.append({"ChannelI" : "I"+str(ch)})

            for i in range(1,41):
                pqs=list()
                U=np.linalg.norm(np.array([float(vals["FFTModule1"]["ACT_FFT"+str(ch)].split(";")[2*i-1]),float(vals["FFTModule1"]["ACT_FFT"+str(ch)].split(";")[2*i])]))
                I=np.linalg.norm(np.array([float(vals["FFTModule1"]["ACT_FFT"+str(ch+4)].split(";")[2*i-1]),float(vals["FFTModule1"]["ACT_FFT"+str(ch+4)].split(";")[2*i])]))
                U=round(U,4)
                I=round(I,4)
                pqs.append(round(float(vals["Power3Module1"]["ACT_HPP"+str(ch)].split(";")[i]),4))
                pqs.append(round(float(vals["Power3Module1"]["ACT_HPQ"+str(ch)].split(";")[i]),4))
                pqs.append(round(float(vals["Power3Module1"]["ACT_HPS"+str(ch)].split(";")[i]),4))
                eleList.append({"HarmValue" : "N;"+str(i)+";U;"+str(U)+";V;I;"+str(I)+";A;P;"+str(pqs[0])+";W;Q;"+str(pqs[1])+";var;S;"+str(pqs[2])+";VA"})

            result["#childs"]=eleList
            endResult.append(result)

        return endResult

    def convertZeraGuiHarmonicPowerChart(self,input,metadata):
        return self.convertZeraGuiHarmonicPowerTable(input,metadata)

    def convertZeraGuiMeterTest(self,input,metadata):
        vals=self.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()

        eleList=self.ActualValuesGeneric(input, metadata)
        eleList.append({"Device-No" : "MT310s2"})
        eleList.append({"AdjustData" : ""})
        eleList.append({"Function" : "Error-Measurement"})
        eleList.append({"Datatype" : "Meter-Error"})
        eleList.append({"Place-No" : ""})
        eleList.append({"RF" : ""})
        eleList.append({"SLambda" : ""})
        eleList.append({"Cz" : str(vals["SEC1Module1"]["PAR_DutConstant"])+";"+str(vals["SEC1Module1"]["PAR_MRate"])+";"+str(vals["SEC1Module1"]["PAR_DUTConstUnit"])})
        eleList.append({"M-Puls" : ""})
        eleList.append({"M-Inp" : ""})
        eleList.append({"Error" : str(vals["SEC1Module1"]["ACT_Result"])})
        eleList.append({"N-Value" : ""})
        eleList.append({"Spread" : ""})
        eleList.append({"Average" : ""})
        eleList.append({"Deviation" : ""})

        result["#childs"]=eleList
        return result

    def convertZeraGuiEnergyComparison(self,input, metadata):
        print("MtVis can not display Energy Comparison Data")

    def convertZeraGuiEnergyRegister(self,input,metadata):
        vals=self.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : ""})
        eleList.append({"Device-Typ" : "MT310s2"})
        eleList.append({"Device-No" : "MT310s2"})
        eleList.append({"AdjustData" : ""})
        datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')
        time=datetimeObj.strftime("%H/%M/%S")
        date=datetimeObj.strftime("%d/%m/%Y")
        eleList.append({"Time" : time})
        eleList.append({"Date" : date})
        URange=float(0)
        IRange=float(0)
        for ch in range(1,4):    
            if URange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                URange=float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1])
            if IRange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                IRange=float(vals["RangeModule1"]["PAR_Channel"+str(ch+4)+"Range"][:-1])

        eleList.append({"U-Range" : str(URange)+";V"})
        eleList.append({"I-Range" : str(IRange)+";A"})
        eleList.append({"M-Mode" : ""})
        eleList.append({"U-PrimSek" : "1"})
        eleList.append({"I-PrimSek" : "1"})
        eleList.append({"PrimSek-Val-Cz-Reg" : ""})
        eleList.append({"Function" : "Register-Test"})
        eleList.append({"Datatype" : "Register-Test"})
        eleList.append({"Place-No" : "1"})
        eleList.append({"Type" : ""})             # wird benötigt  
        eleList.append({"Measurement-Time" : ""}) # wird benötigt
        eleList.append({"Energie" : ""})          # wird benötigt
        eleList.append({"E-Begin" : ""})    # wird benötigt
        eleList.append({"E-End" : ""})      # wird benötigt
        eleList.append({"E-Cz" : ""})       # wird benötigt
        eleList.append({"E-Error" : ""})    # wird benötigt
        eleList.append({"Power" : ""})      # wird benötigt
        eleList.append({"P-Begin" : ""})    # wird benötigt
        eleList.append({"P-End" : ""})      # wird benötigt
        eleList.append({"P-Cz" : ""})       # wird benötigt
        eleList.append({"P-Error" : ""})    # wird benötigt

        result["#childs"]=eleList
        return result

    def convertZeraGuiPowerRegister(self,input, metadata):
        vals=self.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : ""})
        eleList.append({"Device-Typ" : "MT310s2"})
        eleList.append({"Device-No" : "MT310s2"})
        eleList.append({"AdjustData" : ""})
        datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')
        time=datetimeObj.strftime("%H/%M/%S")
        date=datetimeObj.strftime("%d/%m/%Y")
        eleList.append({"Time" : time})
        eleList.append({"Date" : date})
        URange=float(0)
        IRange=float(0)
        for ch in range(1,4):    
            if URange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                URange=float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1])
            if IRange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                IRange=float(vals["RangeModule1"]["PAR_Channel"+str(ch+4)+"Range"][:-1])

        eleList.append({"U-Range" : str(URange)+";V"})
        eleList.append({"I-Range" : str(IRange)+";A"})
        eleList.append({"M-Mode" : ""})
        eleList.append({"U-PrimSek" : "1"})
        eleList.append({"I-PrimSek" : "1"})
        eleList.append({"PrimSek-Val-Cz-Reg" : ""})
        eleList.append({"Function" : "Register-Test"})
        eleList.append({"Datatype" : "Register-Test"})
        eleList.append({"Place-No" : "1"})
        eleList.append({"Type" : ""})             # wird benötigt  
        eleList.append({"Measurement-Time" : ""}) # wird benötigt
        eleList.append({"Energie" : ""})    # wird benötigt
        eleList.append({"E-Begin" : ""})    # wird benötigt
        eleList.append({"E-End" : ""})      # wird benötigt
        eleList.append({"E-Cz" : ""})       # wird benötigt
        eleList.append({"E-Error" : ""})    # wird benötigt
        eleList.append({"Power" : ""})      # wird benötigt
        eleList.append({"P-Begin" : ""})    # wird benötigt
        eleList.append({"P-End" : ""})      # wird benötigt
        eleList.append({"P-Cz" : ""})       # wird benötigt
        eleList.append({"P-Error" : ""})    # wird benötigt

        result["#childs"]=eleList
        return result

    def convertZeraGuiVoltageBurden(self,input, metadata):
        vals=self.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : ""})
        eleList.append({"Device-Typ" : "MT310s2"})
        eleList.append({"Device-No" : "MT310s2"})
        eleList.append({"AdjustData" : ""})
        datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')
        time=datetimeObj.strftime("%H/%M/%S")
        date=datetimeObj.strftime("%d/%m/%Y")
        eleList.append({"Time" : time})
        eleList.append({"Date" : date})
        URange=float(0)
        IRange=float(0)
        
        for ch in range(1,4):    
            if URange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                URange=float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1])
            if IRange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                IRange=float(vals["RangeModule1"]["PAR_Channel"+str(ch+4)+"Range"][:-1])
        

        eleList.append({"U-Range" : str(URange)+";V"})
        eleList.append({"I-Range" : str(IRange)+";A"})
        eleList.append({"M-Mode" : ""})
        eleList.append({"U-PrimSek" : ""})
        eleList.append({"I-PrimSek" : ""})
        eleList.append({"PrimSek-Val-Cz-Reg" : ""})
        eleList.append({"Function" : "U-Burden"})
        eleList.append({"Datatype" : "UBurden-Value"})
        eleList.append({"U-Nominal" : ""})  # wird benötigt
        eleList.append({"B-Nominal" : ""})  # wird benötigt
        eleList.append({"W-Length" : ""})   # wird benötigt 
        eleList.append({"W-Gauge" : ""})    # wird benötigt
        eleList.append({"UPN1" : ""})
        eleList.append({"UPN2" : ""})
        eleList.append({"UPN3" : ""})
        eleList.append({"IL1" : ""})
        eleList.append({"IL2" : ""})
        eleList.append({"IL3" : ""})
        eleList.append({"PHI1" : ""})   # wird benötigt
        eleList.append({"PHI2" : ""})   # wird benötigt
        eleList.append({"PHI3" : ""})   # wird benötigt
        eleList.append({"P1" : ""})
        eleList.append({"P2" : ""})
        eleList.append({"P3" : ""})
        eleList.append({"Q1" : ""})
        eleList.append({"Q2" : ""})
        eleList.append({"Q3" : ""})
        eleList.append({"S1" : ""})
        eleList.append({"S2" : ""})
        eleList.append({"S3" : ""})
        eleList.append({"G1" : ""})
        eleList.append({"G2" : ""})
        eleList.append({"G3" : ""})
        eleList.append({"B1" : ""})
        eleList.append({"B2" : ""})
        eleList.append({"B3" : ""})
        eleList.append({"Y1" : ""})
        eleList.append({"Y2" : ""})
        eleList.append({"Y3" : ""})
        eleList.append({"Sb1" : ""})
        eleList.append({"Sb2" : ""})
        eleList.append({"Sb3" : ""})
        eleList.append({"CosBeta1" : ""})
        eleList.append({"CosBeta2" : ""})
        eleList.append({"CosBeta3" : ""})
        eleList.append({"SN1" : ""})
        eleList.append({"SN2" : ""})
        eleList.append({"SN3" : ""})

        result["#childs"]=eleList
        return result

    def convertZeraGuiCurrentBurden(self,input, metadata):
        vals=self.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : ""})
        eleList.append({"Device-Typ" : "MT310s2"})
        eleList.append({"Device-No" : "MT310s2"})
        eleList.append({"AdjustData" : ""})
        datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')
        time=datetimeObj.strftime("%H/%M/%S")
        date=datetimeObj.strftime("%d/%m/%Y")
        eleList.append({"Time" : time})
        eleList.append({"Date" : date})
        URange=float(0)
        IRange=float(0)
        
        for ch in range(1,4):    
            if URange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                URange=float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1])
            if IRange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                IRange=float(vals["RangeModule1"]["PAR_Channel"+str(ch+4)+"Range"][:-1])
        
        eleList.append({"U-Range" : str(URange)+";V"})
        eleList.append({"I-Range" : str(IRange)+";A"})
        eleList.append({"M-Mode" : ""})
        eleList.append({"U-PrimSek" : "1"})
        eleList.append({"I-PrimSek" : "1"})
        eleList.append({"PrimSek-Val-Cz-Reg" : ""})
        eleList.append({"Function" : "I-Burden"})
        eleList.append({"Datatype" : "IBurden-Value"})
        eleList.append({"I-Nominal" : ""})  # wird benötigt
        eleList.append({"B-Nominal" : ""})  # wird benötigt
        eleList.append({"W-Length" : ""})   # wird benötigt
        eleList.append({"W-Gauge" : ""})    # wird benötigt
        eleList.append({"UPN1" : ""})
        eleList.append({"UPN2" : ""})
        eleList.append({"UPN3" : ""})
        eleList.append({"IL1" : ""})
        eleList.append({"IL2" : ""})
        eleList.append({"IL3" : ""})
        eleList.append({"PHI1" : ""}) # wird benötigt
        eleList.append({"PHI2" : ""}) # wird benötigt
        eleList.append({"PHI3" : ""}) # wird benötigt
        eleList.append({"P1" : ""})
        eleList.append({"P2" : ""})
        eleList.append({"P3" : ""})
        eleList.append({"Q1" : ""})
        eleList.append({"Q2" : ""})
        eleList.append({"Q3" : ""})
        eleList.append({"S1" : ""})
        eleList.append({"S2" : ""})
        eleList.append({"S3" : ""})
        eleList.append({"R1" : ""})
        eleList.append({"R2" : ""})
        eleList.append({"R3" : ""})
        eleList.append({"X1" : ""})
        eleList.append({"X2" : ""})
        eleList.append({"X3" : ""})
        eleList.append({"Z1" : ""})
        eleList.append({"Z2" : ""})
        eleList.append({"Z3" : ""})
        eleList.append({"Sb1" : ""})
        eleList.append({"Sb2" : ""})
        eleList.append({"Sb3" : ""})
        eleList.append({"CosBeta1" : ""})
        eleList.append({"CosBeta2" : ""})
        eleList.append({"CosBeta3" : ""})
        eleList.append({"SN1" : ""})
        eleList.append({"SN2" : ""})
        eleList.append({"SN3" : ""})

        result["#childs"]=eleList
        return result

    def convertZeraGuiInstrumentTransformer(self,input, metadata):
        vals=self.entityComponentSort(input["values"])
        result=dict()
        endResult=list()
        eleList=list()
        eleList.append({"ID" : metadata["session"]})
        eleList.append({"Language" : "DEU"})
        eleList.append({"Device-Typ" : "MT310s2"})
        eleList.append({"Device-No" : "MT310s2"})
        eleList.append({"AdjustData" : ""})
        datetimeObj= datetime.strptime(input["timestemp"], '%a %b %d %H:%M:%S %Y')
        time=datetimeObj.strftime("%H/%M/%S")
        date=datetimeObj.strftime("%d/%m/%Y")
        eleList.append({"Time" : time})
        eleList.append({"Date" : date})
        URange=float(0)
        IRange=float(0)
        
        for ch in range(1,4):    
            if URange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                URange=float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1])
            if IRange < float(vals["RangeModule1"]["PAR_Channel"+str(ch)+"Range"][:-1]):
                IRange=float(vals["RangeModule1"]["PAR_Channel"+str(ch+4)+"Range"][:-1])
        

        eleList.append({"U-Range" : str(URange)+";V"})
        eleList.append({"I-Range" : str(IRange)+";A"})
        eleList.append({"M-Mode" : ""})
        eleList.append({"U-PrimSek" : "1"})
        eleList.append({"I-PrimSek" : "1"})
        eleList.append({"PrimSek-Val-Cz-Reg" : ""})
        eleList.append({"Function" : "UI-Transformer"})
        eleList.append({"Datatype" : "UI-Transformer-Value"})
        eleList.append({"VT-N" : ""})       # wird benötigt
        eleList.append({"VT-X" : ""})       # wird benötigt
        eleList.append({"U-Prim" : ""})     
        eleList.append({"U-Sek-N" : ""})    # wird benötigt
        eleList.append({"U-Sek-X" : ""})    # wird benötigt
        eleList.append({"VT-Value" : ""})
        eleList.append({"VT-Angle-deg" : ""})
        eleList.append({"VT-Angle-min" : ""})
        eleList.append({"VT-Angle-crad" : ""})
        eleList.append({"CT-N" : ""})
        eleList.append({"CT-X" : ""})
        eleList.append({"I-Prim" : ""})     # wird benötigt
        eleList.append({"I-Sek-N" : ""})     # wird benötigt
        eleList.append({"I-Sek-X" : ""})     # wird benötigt
        eleList.append({"CT-Value" : ""})
        eleList.append({"CT-Angle-deg" : ""})
        eleList.append({"CT-Angle-min" : ""})
        eleList.append({"CT-Angle-crad" : ""})
        eleList.append({"VTCT-Value" : ""})
        eleList.append({"VTCT-Angle-deg" : ""})
        eleList.append({"VTCT-Angle-min" : ""})
        eleList.append({"VTCT-Angle-crad" : ""})

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
            ret=func(input,metadata)
            if type(ret) is list:
                for ele in ret:
                    res=dict()
                    res["Result"]=ele
                    endResult.append(res)
            elif type(ret) is dict:
                res=dict()
                res["Result"]=ret
                endResult.append(res)

        return endResult

        
