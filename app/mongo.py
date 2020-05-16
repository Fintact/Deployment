from passlib.hash import pbkdf2_sha256
import pymongo
import uuid

# Establishing the connection
username = "tezindia"
password = "tezos"

srv = "mongodb+srv://{}:{}@supplychain-u6nhl.mongodb.net/test?retryWrites=true&w=majority".format(
    username, password)
client = pymongo.MongoClient(srv)

print("MongoDB Connected")

db = client['Authenication']

FaucetCollection = db['Faucet']
LoginCollection = db['Login']
RequestCollection = db['Request']
SupplierCollection = db['Supplier']
SupplierInvoiceCollection = db['SupplierInvoice']


def Register(email, name, password, category, hashc):
    q1 = {"email": email}
    p = LoginCollection.find(q1)
    check = False

    for i in p:
        if email == i['email']:
            check = True

    if check:
        print("email adress already in database")
        return False
    else:
        password = pbkdf2_sha256.hash(password)
        q2 = {"name": name, "email": email,
              "password": password, 'hash': hashc}
        q2['category'] = category

        # print(q2)
        r = LoginCollection.insert_one(q2)
        return True

def Login(email, password):
    l1 = {"email": email}
    res = LoginCollection.find(l1)

    data = {}
    data['check'] = False
    for i in res:
        if pbkdf2_sha256.verify(password, i['password']):
            data['name'] = i['name']
            data['category'] = i['category']
            data['check'] = True
            data['hash'] = i['hash']
    print(data)
    return data

def AddSupplierRequest(CompanyHash,code,CompanyName):
    l1 = {'hash':code}
    check = False
    res = LoginCollection.find(l1)
    for i in res:
        if i['category'] == "Enterprise":
            check = True 
            
    l2 = {'company':CompanyHash}
    tes = RequestCollection.find(l2)
    
    for i in tes:
        if i['Supplier'] == code:
            check = False
    
    if check:
        l3 = {'company':CompanyName,'Buyer':code,'companyhash':CompanyHash}
        r = RequestCollection.insert_one(l3)
        return True
    return False

def ApprovalStatus(hash):
    l1  =  {'Buyer':hash}
    result = RequestCollection.find(l1)
    data = {}
    for i in result:
        data[i['companyhash']] = i['company']
    print(data)
    return data

def RequestProces(SupplierName,SupplierHash,CompanyHash,check):
    l1  =  {'Buyer':CompanyHash,'companyhash':SupplierHash}
    print(l1)
    result = RequestCollection.delete_one(l1)
    
    if check == 'true':
        l2 = {'CompanyHash':CompanyHash,'SupplierName':SupplierName,'SupplierHash':SupplierHash}
        SupplierCollection.insert_one(l2)

def SupplierData(hash):
    l1 = {'CompanyHash':hash}
    result = SupplierCollection.find(l1)
    data = {}
    counter = 1 
    for i in result: 
        data[counter] = {"SupplierName":i['SupplierName'],"SupplierHash":i['SupplierHash']}
    print(data)
    return data 

def AddKey(name):
    l1 = {'Name':name}
    FaucetCollection.insert_one(l1)
    print("Key Inserted")

def AddInvoice(SupplierHash,InvoiceText,DelDate,PaymentDate,InvoiceNumber,InvoiceType,EnterpriseHash,EnterpriseName,Amount):
    l1 = {'Hash':SupplierHash,'InvoiceText':InvoiceText,
    'DelDate':DelDate,"PaymentDate":PaymentDate,"InvoiceNumber":InvoiceNumber,
    'InvoiceType':InvoiceType,
    'EnterpriseHash':EnterpriseHash,
    "EnterpriseName":EnterpriseName,'Amount':Amount,
    "Status":"Supplier",
    "Id":str(uuid.uuid4())
    }
    SupplierInvoiceCollection.insert(l1)

def DynamicInvoiceData(hash):
    l1 = {'Hash':hash,'InvoiceType':'DynamicDiscounting'}
    result = SupplierInvoiceCollection.find(l1)
    data = {}
    counter = 1   
    for i in result:
        data[counter] = {'EnterpriseName':i['EnterpriseName'],'DelDate':i['DelDate'],'PaymentDate':i['PaymentDate'],'Amount':i['Amount'],
        'InvoiceText':i['InvoiceText'],'Id':i['Id'],'Status':i['Status']}
        
        if  i['Status'] == "Enterprise" or i['Status'] == 'Final':
            data[counter]['capital'] = i['capital']
            data[counter]['Margin'] = i['Margin']
        counter += 1 
    return data 

def RemoveInvoice(id):
    l1 = {'Id':id}
    SupplierInvoiceCollection.delete_one(l1)

def UpdateDynamicInvoice(name,margin,capital,id):
    l1 = {'Id':id}
    l2 = { "$set": { "Supplier":name,"Margin":margin,"capital":capital,'Status':'Enterprise' } }
    SupplierInvoiceCollection.update_one(l1,l2)

def UpdateMarketInvoice(name,capital,id):
    l1 = {'Id':id}
    l2 = { "$set": { "Supplier":name,"capital":capital,'Status':'Enterprise' } }
    SupplierInvoiceCollection.update_one(l1,l2)


def DynamicEnterpriseData(hash):
    l1  = {'EnterpriseHash':hash,'InvoiceType':'DynamicDiscounting'}
    result  =  SupplierInvoiceCollection.find(l1)
    print(l1)
    data = {}
    counter = 1   
    for i in result:
        if  i['Status'] == 'Enterprise' or i['Status'] == 'Final':
            data[counter] = {'Supplier':i['Supplier'],'DelDate':i['DelDate'],'PaymentDate':i['PaymentDate'],'Amount':i['Amount'],
            'InvoiceText':i['InvoiceText'],'Id':i['Id'],'Capital':i['capital'],'Margin':i['Margin'],'Status':i['Status']}
            data[counter]['Remain'] = str(int(int(i['Amount']) -  (int(i['Amount'])*int(i['Margin']))/100))
        elif i['Status'] == 'Supplier':
             data[counter] = {'SupplierHash':i['Hash'],'DelDate':i['DelDate'],'PaymentDate':i['PaymentDate'],'Amount':i['Amount'],
            'InvoiceText':i['InvoiceText'],'Id':i['Id'],'Status':i['Status']}
        counter += 1 
    return data 

def MarketEnterpriseData(hash):
    l1  = {'EnterpriseHash':hash,'InvoiceType':'RequestWorkingCapital','Status':'Enterprise'}
    result  =  SupplierInvoiceCollection.find(l1)
    print(l1)
    data = {}
    counter = 1   
    for i in result:
        data[counter] = {'Supplier':i['Supplier'],'DelDate':i['DelDate'],'PaymentDate':i['PaymentDate'],'Amount':i['Amount'],
        'InvoiceText':i['InvoiceText'],'Id':i['Id'],'Capital':i['capital']}
        counter += 1 
    return data 

def MarketInvoiceData(hash):
    l1 = {'Hash':hash,'InvoiceType':'RequestWorkingCapital'}
    result = SupplierInvoiceCollection.find(l1)
    data = {}
    counter = 1   
    for i in result:
        data[counter] = {'EnterpriseName':i['EnterpriseName'],'DelDate':i['DelDate'],'PaymentDate':i['PaymentDate'],'Amount':i['Amount'],
        'InvoiceText':i['InvoiceText'],'Id':i['Id'],'Status':i['Status']}
        if  i['Status'] == "Enterprise":
            data[counter]['capital'] = i['capital']
           
        counter += 1 
    return data 

def MarketShip(Id,Interest):
    l1 = {'Id':Id}
    l2 = { "$set": {"Interest":Interest,'Status':'Market' } }
    SupplierInvoiceCollection.update_one(l1,l2)

def DynamicPayment(Id):
    l1 = {'Id':Id}
    capital = 0 
    SenderCode = ""
    result = SupplierInvoiceCollection.find(l1)
    for  i in result:
        capital = int(i['capital'])
        SenderCode = i['Hash']

    l2 = {'Id':Id}
    l3 = { "$set": {'Status':'Final' } }
    SupplierInvoiceCollection.update_one(l2,l3)

    return capital,SenderCode