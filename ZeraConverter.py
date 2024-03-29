#!/usr/bin/python

#Systemmodules
import sys
import getopt

#custom imports
from pythonconverter_pkg import ConversionUnit as con

def enum(**enums):
    return type('Enum', (), enums)

useDef = enum(Help=0, ShowSessions=2, ShowTransactions=3, Convert=4)

inputFile = ""
outputFile = ""
userscript = ""
conversionType = "sql2xml"
session = ""
parameters = ""
usecase = useDef.Help
gui = False
converter = object
filterExp = ""

def Help():
    print("USAGE:")
    print("#################")
    print("Show this Help:")
    print("    ./Converter")
    print("Show available records:")
    print(" ./Converter -i <file>.db")
    print("Convert file")
    print("    ./Convert -i <file>.db -o <file>.xml --session=<sessionName>")

def main(argv):
    global inputFile
    global outputFile
    global userscript
    global conversionType
    global filterExp
    global session
    global usecase
    global gui
    global converter
    global parameters

    retVal = 0

    print("Database Converter")

    try:
        opts, args = getopt.getopt(argv,"dghi:o:t:",["ifile=","ofile=","eparam=","session="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputFile = arg
        elif opt in ("-o", "--ofile"):
            outputFile = arg
        elif opt in ("--session"):
            session = arg
        elif opt in ("--eparam"):
            parameters = arg
        elif opt == "-d":
            # debug
            inputFile = "./test/test.db"
            outputFile = "./test/out.xml"
            session= "ses1all"
            userscript= "zeraconverterengines.MTVisRes"
            filterExp="Snapshot"
            parameters="{'digits' : '8', 'decimalPlaces' : '2', 'local' : 'DE'}"

        converter = con.ConversionUnit()

    print('Input file is ', inputFile)
    print('Output file is ', outputFile)

    #define usecase depending on input data
    usecase = useDef.Help
    if inputFile != "" :
        usecase=useDef.ShowSessions
        if session != "" and inputFile != "" and outputFile != "":
            usecase=useDef.Convert

        if usecase != useDef.Help:
            try:
                if converter.seteParam(parameters) == False:
                    raise Exception("set parameter error")
                if converter.setInputFile(inputFile) == False:
                    raise Exception("set input file error")
                if converter.setOutputFile(outputFile) == False:
                    raise Exception("set output file error")
                if converter.setFilter(filterExp) == False:
                    raise Exception("set Filter Error")
                if converter.setUserScript(userscript) == False:
                    raise Exception("Load Userscript error")
                if converter.convert(session) == False:
                    raise Exception("Conversion Error")
            except Exception as error:
                print("Fatal Error:", error)
            retVal = converter.getErrorRegister() | (converter.getUserScriptErrors() << 16)
            print(bin(retVal))
            return retVal

    if usecase == useDef.Help:
        Help()
    elif usecase == useDef.ShowSessions:
        ret = converter.ShowSessions()
        i=0
        for ele in ret :
            print(i,": ",ele[0])
            i=i+1
    elif usecase == useDef.Convert:

        retVal=converter.convert(session)
    print("Programm ended with "+str(retVal))
    return retVal

if __name__ == "__main__":
    main(sys.argv[1:])
