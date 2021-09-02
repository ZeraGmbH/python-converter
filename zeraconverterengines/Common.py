from datetime import datetime
import math
import re

# @input inputMap

# @output Static session data as dict
def getStatic(input):
    try:
        keys = [k  for  k in input.keys()]
        return input[keys[0]]["static"]
    except:
        return ""

# @input inputMap
# @output dynamic session data
def getDynamic(input):
    try:
        keys = [k  for  k in input.keys()]
        return input[keys[0]]["dynamic"]
    except:
        return ""

# @input inputMap
# @output transaction list
def getTransactions(input):
    try:
        keys = [k  for  k in input.keys()]
        return input[keys[0]]["dynamic"].keys()
    except:
        return list()

# @input  dynamic Session data
# @input transaction name

# @output transactionData dict

def getTransactionData(input, transaction):
    try:
        keys = [k  for  k in input.keys()]
        return input[keys[0]]["dynamic"][transaction]
    except:
        return ""

# @input transactionData
# @outpur entityComponent map with value
def entityComponentSort(input):
    result=dict()
    for ele in input:
        compDict=dict()
        if ele["entity_name"] in result:
            compDict=result[ele["entity_name"]]
        compDict[ele["component_name"]] = ele["component_value"]
        result[ele["entity_name"]]=compDict
    return result

# @input dict
# @ output dict value or ""
def readSafe(vals,parList):
    tmp=vals[parList[0]]
    parList.pop(0)
    for l in parList:
        if l in tmp:
            tmp=tmp[l]
        else:
            return ""
    if tmp==None:
        return ""

    return tmp

def UnitNumberSeperator(string):
    retVal=dict()
    retVal["value"]=0
    retVal["unit"]=""
    try:
        exp=re.match("^([aA-zZ]*)([-+]{0,1})([1-9]{1,1}[0-9]*[\.,]{0,1}[0-9]*)\s*([aA-zZ]*)$",string)
        tmp=str(exp.group(2))+str(exp.group(3))
        tmp=tmp.replace(",",".")
        retVal["value"]=float(tmp)
        retVal["unit"]=exp.group(4)
    except :
        retVal["value"]=0
        retVal["unit"]=""
    return retVal
