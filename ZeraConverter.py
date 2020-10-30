#!/usr/bin/python

#Systemmodules
import sys, getopt
import tkinter as tk
import tkinter.filedialog
from tkinter.messagebox import showinfo

#custom imports
from pythonconverter_pkg import ConversionUnit as con

#testimports
from pythonconverter_pkg import XmlInterface as zxml

def enum(**enums):
    return type('Enum', (), enums)

useDef = enum(Help=0, ShowRecords=2, ShowTransactions=3, Convert=4)

root= tk.Tk()

inputFile = ""
outputFile = ""
userscript= ""
conversionType="sql2xml"
record= ""
usecase = useDef.Help
gui = False
converter = object




def guiApp():
	inputTb=""
	outputTb=""
	engineTb=""
	sessionTb=""
	def inputfileSearch():
		global inputFile
		inputFile=tk.filedialog.askopenfilename()
		inputTb.delete(1.0,"end")
		inputTb.insert(1.0,inputFile)
	def outputfileSearch():
		global outputFile
		filename=tk.filedialog.asksaveasfile()
		outputFile=filename.name
		outputTb.delete(1.0,"end")
		outputTb.insert(1.0,outputFile)
	def enginefileSearch():
		global userscript
		userscript=tk.filedialog.askopenfilename()
		engineTb.delete(1.0,"end")
		engineTb.insert(1.0,userscript)
	def findRecords():
		global record
		global converter
		converter.setInputFile(inputFile)
		ret = converter.ShowRecords()
		i=0
		for ele in ret :
			showinfo("Sessions",ele[0])
			print(i,": ",ele[0])
			i=i+1

	def convert():
		global record
		record=sessionTb.get(1.0,"end").rstrip('\n')
		record
		root.destroy()
		


	inputl=tk.Label(root,text="Database")
	inputTb=tk.Text(root,height=1,width=60)
	inputSb=tk.Button(root,text="search", command=inputfileSearch)
	outputl=tk.Label(root,text="export file path")
	outputTb=tk.Text(root,height=1,width=60)
	outputSb=tk.Button(root,text="search",command=outputfileSearch)
	sessionl=tk.Label(root,text="session")
	sessionTb=tk.Text(root,height=1,width=60)
	sessionSb=tk.Button(root,text="sessions",command=findRecords)
	enginel=tk.Label(root,text="conversion engine")
	engineTb=tk.Text(root,height=1,width=60)
	engineSb=tk.Button(root,text="search",command=enginefileSearch)
	convertB=tk.Button(root,text="CONVERT",command=convert)

	inputl.grid(row=0)
	inputTb.grid(row=1,column=0)
	inputSb.grid(row=1,column=1)
	outputl.grid(row=2)
	outputTb.grid(row=3,column=0)
	outputSb.grid(row=3,column=1)
	sessionl.grid(row=4)
	sessionTb.grid(row=5,column=0)
	sessionSb.grid(row=5,column=1)
	enginel.grid(row=6)
	engineTb.grid(row=7,column=0)
	engineSb.grid(row=7,column=1)
	convertB.grid(row=8)

	inputTb.insert(1.0,inputFile)
	outputTb.insert(1.0,outputFile)
	engineTb.insert(1.0,userscript)
	sessionTb.insert(1.0,record)

	root.mainloop()




def Help():
	print("USAGE:")
	print("#################")
	print("Show this Help:")
	print("	./Converter")
	print("Show available records:")
	print(" ./Converter -i <file>.db")
	print("Convert file")
	print("	./Convert -i <file>.db -o <file>.xml --session=<sessionName>")
	print("Start with gui")
	print("	./Converter -g")


def main(argv):
	global inputFile
	global outputFile
	global userscript
	global conversionType
	global record
	global usecase
	global gui
	global converter

	print("Database Converter")
	

	try:
		opts, args = getopt.getopt(argv,"dghi:o:t:",["ifile=","ofile=","record="])
	except getopt.GetoptError:
		print('test.py -i <inputfile> -o <outputfile>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('test.py -i <inputfile> -o <outputfile>')
			sys.exit()
		elif opt == "-g":
			gui = True
		elif opt in ("-i", "--ifile"):
			inputFile = arg
		elif opt in ("-o", "--ofile"):
			outputFile = arg
		elif opt in ("--session"):
			record = arg
		elif opt == "-d":
                        inputFile = "./test/test.db"
                        outputFile = "./test/out.xml"
                        #userscript= "./zeraconverterengines/MTVisRes.py"
                        record= "[customer ID is not set] 2020/10/27"
                        userscript= "zeraconverterengines.MTVisRes2"

		converter = con.ConversionUnit()
	if gui == True:
		guiApp()

	print('Input file is ', inputFile)
	print('Output file is ', outputFile)

	#define usecase depending on input data
	usecase=useDef.Help
	if inputFile != "" :
		usecase=useDef.ShowRecords
		if record != "" and inputFile != "" and outputFile != "":
			usecase=useDef.Convert

	try:
		if usecase != useDef.Help:
			converter.setInputFile(inputFile)
			converter.setOutputFile(outputFile)
			converter.setType(conversionType)
			if converter.setUserScript(userscript) == False:
				raise Exception()
	#converter.setConfigFile(configFile)
	except:
                print("engine import error")
                return None

		
	if usecase == useDef.Help:
		Help()
	elif usecase == useDef.ShowRecords:
		ret = converter.ShowRecords()
		i=0
		for ele in ret :
			print(i,": ",ele[0])
			i=i+1
	elif usecase == useDef.Convert: 
		converter.convert(record)


if __name__ == "__main__":
	main(sys.argv[1:])
