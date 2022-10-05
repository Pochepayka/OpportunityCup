import os
import json
import re
import datetime
from symbol import decorated
# from filtersFunc import globalFilters

class OperationData:
    propertyNames = ['date', 'card', 'account', 'accountValidTo', 'client', 'lastName',
                        'firstName', 'patronymic', 'dateOfBirth', 'passport', 'passportValidTo', 'phone', 
                        'operType', 'amount', 'operResult', 'terminal', 'terminalType', 'city', 'address']
    def __init__(self, objectValueList):
        self._rank = 20
        if len(objectValueList) != len(OperationData.propertyNames):
            raise ValueError("Bad data length")
        for i in range(len(objectValueList)):
            value = objectValueList[i]
            if value is not None: 
                key = OperationData.propertyNames[i]
                setattr(self, key, value)
    def toJSON(self):
        return json.dumps(self, default = lambda o: f"{o.__dict__}", indent = 2)
    def set_rank(self, rank):
        self._rank = rank
    def get_rank(self):
        return self._rank
    def __str__(self):
        return "OperationData(%s)" % ','.join([key + ": " + str( getattr(self, key)) for key in OperationData.propertyNames])
    def __repr__(self):
        return str(self)



def readJsonFile(objectsList = []):
    jsonFile = open(f'{os.path.dirname(os.getcwd())}/transactions.json', encoding='utf-8')
    jsonObject = json.load(jsonFile)
    for numberObj, DataObject in enumerate(jsonObject["transactions"]):
        objectValueList = []
        for key in jsonObject["transactions"][DataObject]:
            objectValueList.append(jsonObject["transactions"][DataObject][key])
        objectsList.append(OperationData(objectValueList))
    jsonFile.close()
    return objectsList

def repeatCard(objectsList):
    sameCards = dict()
    for object in objectsList:
        if object.card not in sameCards:
            sameCards.update({object.card: [object]}) 
        else: 
            sameCards[object.card].append(object)
    return sameCards

def outputDictTerminal(dict):
    for key, value in dict.items():
        if(len(value) > 1):
            print( '\n\n', '----------next-------------', '\n\n', 'Количество повторяющихся операций:', len(value))
            for operation in value:
                print('\n')
                for item, val in operation.__dict__.items():
                    print(item, val)

def objToJson(object):
    JSON = json.dumps(object.toJSON())
    JSON = re.sub(r',', lambda o: ',\n', str(object))
    return (JSON + '\r\n')

def reduceRank(object, quantity): #универсальная функция, уменьшающая приоритетность операции 
    object.set_rank(object.get_rank()-quantity)

def strToTime(strTime): #универсальная функция, переводит строку во время
    return datetime.datetime.strptime(strTime, "%H:%M:%S").time()

def tryExceptDecorator(): #дописать декоратор для changeObjDates()
    def _wrapper(returnDate):
        try: 
            return datetime.datetime.strptime(returnDate, "%Y-%m-%dT%H:%M:%S")
        except:
            return datetime.datetime.strptime(returnDate, "%Y-%m-%d")
    return _wrapper


def changeObjDates(list): #нужна для переопределения строк в объекте на объект даты
    for object in list:
        object.date = datetime.datetime.strptime(object.date, "%Y-%m-%dT%H:%M:%S")
        # exit() # тут дописать декоратор
        try:
            object.passportValidTo = datetime.datetime.strptime(object.passportValidTo, "%Y-%m-%dT%H:%M:%S")
        except:
            object.passportValidTo = datetime.datetime.strptime(object.passportValidTo, "%Y-%m-%d")
        try:
            object.dateOfBirth = datetime.datetime.strptime(object.dateOfBirth, "%Y-%m-%dT%H:%M:%S")
        except:
            object.dateOfBirth = datetime.datetime.strptime(object.dateOfBirth, "%Y-%m-%d")
        try:
            object.accountValidTo = datetime.datetime.strptime(object.accountValidTo, "%Y-%m-%dT%H:%M:%S")
        except: 
            object.accountValidTo = datetime.datetime.strptime(object.accountValidTo, "%Y-%m-%d")

def impossibleValues(object):
    yearFromPass = int(f"{object.passport}"[2:4]) #выяснили год пасспорта
    yearFromBirth = int(f"{object.dateOfBirth}"[0:4]) 
    terminal = object.terminal[0:3]

    if(terminal == "POS" and object.operType == "Пополнение"):#пополнение через POS
        reduceRank(object, 2) 

    if(((object.date.time() >= strToTime("22:00:00")) and 
        (object.date.time() <= strToTime("23:59:59"))) or
        ((object.date.time() >= strToTime("00:00:00")) and
        (object.date.time() <= strToTime("06:00:00")))):
            reduceRank(object, 1)

def globalFilters(objectsList):
    for object in objectsList: 
        if object.get_rank() > 0: #если у нас уже есть в базе фрод, не будем запускать
            impossibleValues(object)
        print(object.get_rank()) if (object.get_rank() < 20) else object
    # with open('./testFile.txt', 'w+', encoding = 'utf-8') as output:
    #     for object in objectsList:
    #         if object.operResult == 'Отказ':
    #             output.write(objToJson(object))


def __main__():
    objectsList = readJsonFile([])  #получаем список json объектов
    changeObjDates(objectsList) #заменяем строковые даты на объекты дат
    globalFilters(objectsList) #основная фильтрующая функция
    repeatCards = repeatCard(objectsList) #получаем список словарей с уникальными ключами в виде номеров карт
    # outputDictTerminal(repeatCards)
        


__main__()