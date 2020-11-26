
#Systemmodules
import sys
from pathlib import Path

#Custom moudles
from pythonconverter_pkg import ConversionUnit as con


inputFile =""
outputFile=""
engine=""
session=""
params=""

def setInputPath(p_path):
    global inputFile
    inputFile=p_path

def setOutputPath(p_path):
    global outputFile
    outputFile=p_path

def setEngine(p_path):
    global engine
    engine=p_path

def setSession(p_session):
    global session
    session=p_session

def setParams(p_params):
    global params
    params=p_params

def checkInputFile():
    retVal=False
    my_file = Path(inputFile)
    if my_file.is_file():
        retVal=True

    return retVal

def checkEngine():
    retVal=False
    my_file = Path(engine)
    if my_file.is_file():
        retVal=True
    return retVal

def convert():
    print(inputFile)
    print(outputFile)
    print(engine)
    print(params)
    if(checkInputFile() ==False):
        return False
    try:       
        converter = con.ConversionUnit()
        converter.seteParam(params)
        converter.setInputFile(inputFile)
        converter.setOutputFile(outputFile)
        if converter.setUserScript(engine) == False:
            return False
        converter.convert(session)
    except:
        return False
    return True
