import re, os
import collections
import zipfile
from collections import OrderedDict

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            if not(file.endswith('.zip')):
                ziph.write(os.path.join(root, file))
                os.remove(os.path.join(root, file))

def combineDataToFreqs(data, freqs):
    if data == None or freqs == None:
        return None
    
    for dataId in data:
        
        #delete what must
        if dataId not in combined:
            capsulated = dict()
        else:
            capsulated=combined[dataId]
        
        if dataId in (data, freqs):
            capsulated['data'].extend(data[dataId])
            capsulated['frequency'] += freqs[dataId]
        
        if dataId in combined:
            combined[dataId]=capsulated
        else:
            combined.update({dataId:capsulated})
    
    return combined   

    def incrementDigitValue(self, dictionary, field, fieldData, dictIncrement):
        increment = 0
        if field in dictIncrement:
            increment = dictIncrement[field]
        else:
            print("Nothing to increment! Key "+field+" not found for dictionary "+str(dictIncrement))
            
        if field in dictionary:
            dictionary[field] += increment
        else:
            dictionary[field] = increment
            
        if fieldData in dictionary and fieldData in dictIncrement:
            keyValuePair = dict()
            for value in dictIncrement[fieldData]:
                if not(value in dictionary[fieldData]):
                    keyValuePair[value]=1
                else:
                    keyValuePair[value]+=1
            dictionary[fieldData].append(keyValuePair)
        return dictionary
            

    def appendMatchesInDictionary(self, targetDictionary, targetKey, newMatchesDict):
        if targetDictionary == None:
            targetDictionary = dict()
        if not(targetKey in targetDictionary):
            data = dict()
        else:
            data = targetDictionary[targetKey]
        
        for matchKey in newMatchesDict:
            dataValue = None
            if matchKey in data:
                if newMatchesDict[matchKey]==data[matchKey]:
                    data[matchKey]=incrementDigitValue(data[matchKey], 'frequency', 'data', newMatchesDict[matchKey])
                    continue
                dataValue = data[matchKey]
            elif not (matchKey in data):
                dataValue = []
            dataValue.append(newMatchesDict[matchKey])
            data[matchKey] = dataValue
            
        targetDictionary[targetKey]=data
        return targetDictionary[targetKey] 

def getDictValue(x, key):
    value=""
    try:
        if key in x:
            value = x[key]
        return value
    except TypeError as err:
        print(err)
        print("Unexpected error for structure "+x+" with key "+key)
    except:
        print("Unexpected error for structure "+x+" with key "+key)
    return value

def fixToFIleNameFormat(parr):
    strVal=""
    if parr.find("-") == True:
        keyArr = parr.split("-")
        for val in keyArr:
            #val = keyArr[key]
            if len(strVal) < 1:
                strVal += val.zfill(2)
            else:
                strVal += "_" + val.zfill(2)
    
    else:
        strVal = parr.zfill(2)
        
    return strVal

def getKeyAndValuePair(field,result,key):
    value=""
    if field in result:
        x = result[field]
        value = getDictValue(x, key)
    return value

def convertToInt(p):
        if len(p) > 0:
            p = int(p)
        else:
            p = 0
        return p
    
def contains_digits(d):
    _digits = re.compile('\d')
    return bool(_digits.search(d))