
#Systemmodules
import sys
from pathlib import Path
import warnings
import logging

#Custom moudles
from pythonconverter_pkg import ConversionUnit as con


inputFile =""
outputFile=""
engine=""
session=""
params=""
filterExp=""

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

def setFilter(p_filter):
    global filterExp
    filterExp=p_filter

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
    retVal=0
    print(inputFile)
    print(outputFile)
    print(engine)
    print(filterExp)
    print(params)
    if checkInputFile() == False:
        return 2 # open database error
    try:       
        converter = con.ConversionUnit()
        if converter.seteParam(params) == False:
            raise Exception("set parameter error")
        if converter.setInputFile(inputFile) == False:
            raise Exception("set input file error")
        if converter.setOutputFile(outputFile) == False:
            raise Exception("set output file error")
        if converter.setFilter(filterExp) == False:
            raise Exception("set Filter Error")
        if converter.setUserScript(engine) == False:
            raise Exception("Load Userscript error")
        if converter.convert(session) == False:
            raise Exception("Conversion Error")
    except Exception as error:
        logging.warning("Fatal Error: ",  error)
    retVal = converter.getErrorRegister() | (converter.getUserScriptErrors() << 16)
    return retVal
