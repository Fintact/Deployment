from flask import Flask, render_template, request, redirect, url_for, session
import mongo
import hashlib
import os
import tezos 
port = int(os.environ.get("PORT", 5000))

app = Flask(__name__, static_url_path='/static')

app.debug = True
app.secret_key = "Nothing"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    if 'name' in session:
        if session['category'] == "Investor":
            return redirect("/capital")
        else: 
            return redirect("/company")
    return render_template("login.html")

@app.route("/company")
def Company():
    if 'name' in session:
        if session['category'] == "Investor":
            return redirect("/capital")
        data = mongo.SupplierData(session['hash'])
        balance = tezos.GetBalance(session['hash'])
        print(balance)
        return render_template('/company/index.html',name=session['name'],data=data,hash=session['hash'],balance=balance['balance'])
    return redirect("/")

@app.route("/company/request")
def CompanyRequest():
    if 'name' in session:
        if session['category'] == "Investor":
            return redirect("/capital")
        return render_template('/company/request.html',name=session['name'])
    return redirect("/")

@app.route("/company/approve")
def CompanyApprove():
    if 'name' in session:
        if session['category'] == "Investor":
            return redirect("/capital")
        data =  mongo.ApprovalStatus(session['hash'])
        return render_template("/company/approval.html",name=session['name'],data=data)
    return redirect("/")

@app.route("/company/supplier/dynamic")
def DynamicInvoice():
    if 'name' in session:
        if session['category'] == "Investor":
            return redirect("/capital")
        
        data = mongo.DynamicInvoiceData(session['hash'])
        print(data)
        return render_template("/company/dynamic.html",name=session['name'],data=data)
    return redirect("/")

@app.route("/company/enterprise/dynamic")
def DynamicApprove():
    if 'name' in session:
        if session['category'] == "Investor":
            return redirect("/capital")
        
        data = mongo.DynamicEnterpriseData(session['hash'])
        print(data)
        return render_template("/company/dynamic-approve.html",name=session['name'],data=data)
    return redirect("/")

@app.route("/company/enterprise/market")
def MarketEnterpriseApprove():
    if 'name' in session:
        if session['category'] == "Investor":
            return redirect("/capital")
        
        data = mongo.MarketEnterpriseData(session['hash'])
        print(data)
        return render_template("/company/market-enterprise.html",name=session['name'],data=data)
    return redirect("/")

@app.route("/company/supplier/market")
def  SupplierMarketSection():
    if 'name' in session:
        if session['category'] == "Investor":
            return redirect("/capital")
        
        data = mongo.MarketInvoiceData(session['hash'])
        print(data)
        return render_template("/company/market-supplier.html",name=session['name'],data=data)
    return redirect("/")

@app.route("/company/createinvoice")
def CompanyCreate():
    if 'name' in session:
        if session['category'] == "Investor":
            return redirect("/capital")
        data = mongo.SupplierData(session['hash'])
        print("Invoice",data)
        return render_template("/company/invoice-create.html",name=session['name'],data=data)
    return redirect("/")


@app.route("/capital")
def Investor():
    if 'name' in session:
        if session['category'] == "Enterprise":
            return redirect("/company")
        return render_template('/investor/index.html',name=session['name'])
    return redirect("/")


# Ajax Routes
@app.route('/login_action', methods=['POST'])
def login_action():

    email = request.form['email']
    password = request.form['password']
    print(email, password)
    data = mongo.Login(email, password)

    link_map = {"Investor": '/capital',"Enterprise":"/company"}

    if data['check']:
        data['link'] = link_map[data['category']]
        session['name'] = data['name']
        session['category'] = data['category']
        session['hash'] = data['hash']
        return data
    return data

@app.route('/sign_action', methods=['POST'])
def sign_action():

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    category = request.form['category']
    hash_object = hashlib.sha1(email.encode())
    hashc = hash_object.hexdigest()[-15:]

    
    link_map = {"Investor": '/capital',"Enterprise":"/company"}

    data = {}
    data['check'] = False
    print(hashc,name,email,category)
    if mongo.Register(email, name, password, category, hashc):

        data['check'] = True
        data['link'] = link_map[category]

        session['name'] = name
        session['category'] = category
        session['hash'] = hashc
        return data

    return data

@app.route('/supplier_action',methods=['POST'])
def SupplierAction():

    code = request.form['code']
    print(code)
    data = {}
    data['check'] = False
    if mongo.AddSupplierRequest(session['hash'],code,session['name']):
        data['check'] = True
    return data

@app.route('/company/submit', methods=['POST'])
def company_submit():
    hashcode = request.form['HashCode']
    flag = request.form['flag']
    name = request.form['Name']
    print(hashcode,flag,name,session['hash'])
    mongo.RequestProces(name,hashcode,session['hash'],flag)
    return "asd"

@app.route("/create_invoice",methods=['POST'])
def Create_Invoice():
    InvoiceText = request.form['InvoiceText']
    DelDate = request.form['DelDate']
    PaymentDate =  request.form['PaymentDate']
    Supplier = request.form['Supplier']
    InvoiceNumber = request.form['InvoiceNumber']
    InvoiceType = request.form['InvoiceType']
    Currency = request.form['Currency']

    mongo.AddInvoice(Supplier,InvoiceText,DelDate,PaymentDate,InvoiceNumber,InvoiceType,session['hash'],session['name'],Currency)
    print(DelDate,PaymentDate,Currency,InvoiceText,InvoiceType,InvoiceNumber,Supplier)
    return "ada"

@app.route("/company/dynamicreject",methods=['POST'])
def DynamicReject():
    Id =  request.form['Id']
    mongo.RemoveInvoice(Id)
    print(Id)
    return "asd"

@app.route("/company/dynamic/approve",methods=['POST'])
def DynamicApproveSupplier():
    Id = request.form['Id']
    Margin = request.form['Margin']
    Capital = request.form['Capital']
    print(Id,Margin,Capital)
    mongo.UpdateDynamicInvoice(session['name'],Margin,Capital,Id)
    return "asd"

@app.route("/company/market/approve",methods=['POST'])
def MarketApproveSupplier():
    Id = request.form['Id']
    Capital = request.form['Capital']
    print(Id,Capital)
    mongo.UpdateMarketInvoice(session['name'],Capital,Id)
    return "asd"


@app.route("/company/dynamic/payment",methods=['POST'])
def DynamicPayment():
    Id = request.form['Id']
    amount,recieverhash = mongo.DynamicPayment(Id)
    print(Id,amount,recieverhash)
    return "asd"

@app.route("/company/dynamic/remain",methods=['POST'])
def DynamicRemain():
    Id = request.form['Id']
    return "asd"

@app.route("/company/market/ship",methods=['POST'])
def MarketShip():
    Id =  request.form['Id']
    Interest =  request.form['Interest']
    print(Id,Interest)
    mongo.MarketShip(Id,Interest)
    return "asd"

@app.route("/logout")
def LogOut():
    session.clear()
    return redirect("/")

@app.errorhandler(404)
def error404(error):
    return render_template('404.html'), 404
    
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=port)
