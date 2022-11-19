from __future__ import print_function
from flask import Flask,render_template,request,redirect,url_for,session
import ibm_db
import re

import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

app=Flask(__name__)

app.secret_key='a'

print("plasma")

conn= ibm_db.connect("DATABASE=bludb;HOSTNAME=2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30756;SECURITY=SSL;SSLSeverCertificate=DigiCertGlobalRootCA.crt;UID=jzl90633;PWD=PePE5tTa82TLL98S",'','')

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    

sql ="select * from Count_Values"
stmt=ibm_db.exec_immediate(conn,sql)
ibm_db.fetch_row(stmt)

donor_count =ibm_db.result(stmt,0)
request_count = ibm_db.result(stmt,1)
userid =''

@app.route('/')
def home():
    return render_template('Register_1.html')

@app.route('/request_page',methods=['GET','POST'])
def request_page():
    msg=''
    if request.method == 'POST':
        blood_type=request.form['blood_type']
        userid= session['USERNAME']
        insert_sql="select * from DONORS"
        mail_sql="select * from DONORS where USERNAME='%s'"%(userid)
        record=ibm_db.exec_immediate(conn,insert_sql)
        record2=ibm_db.exec_immediate(conn,mail_sql)
        ibm_db.fetch_row(record2)
        name_list =ibm_db.fetch_assoc(record)
        html_content = "<html><body><h1>Plasma Donation</h1><p>%s blood was request.Contect info: <br>Email id:%s,<br>Mobile NO:%s,<br>Address:%s.</p></body></html>"%(blood_type ,ibm_db.result(record2,1),ibm_db.result(record2,3),ibm_db.result(record2,5))
        while name_list != False:
            email=name_list["EMAIL"]
            name=name_list["USERNAME"]
            subject = "Hello "+name
           
            sender = {"name":"Plasma Donor Apllication","email":"Hello@gmail.com"}
            to = [{"email":email,"name":name}]
            cc = [{"email":email,"name":name}]
            bcc = [{"name":name,"email":email}]
            reply_to = {"email":email,"name":name}
            headers = {"Some-Custom-Name":"unique-id-1234"}
            params = {"parameter":"plasma donor application","subject":"plasma donation"}
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, bcc=bcc, cc=cc, reply_to=reply_to, headers=headers, html_content=html_content, sender=sender, subject=subject)
        
            print(name)
            try:
                api_response = api_instance.send_transac_email(send_smtp_email)
                pprint(api_response)
                msg="Request success"
            except ApiException as e:
                print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
            name_list =ibm_db.fetch_assoc(record)
        return render_template('/login.html',msg=msg)

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    msg=''
    if request.method == 'POST':
        age=request.form['age']
        R_value = request.form['R_button']
        userid= session['USERNAME']
        insert_sql="update DONORS set AGE=?,STATUS=? where USERNAME=?"
        prep_stmt=ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(prep_stmt,1,age)
        ibm_db.bind_param(prep_stmt,2,R_value)
        ibm_db.bind_param(prep_stmt,3,userid)
        
        if R_value == "donor":
            if age >= '17' and age <= '60':
                ibm_db.execute(prep_stmt)
                return render_template('Request.html')
                
            else:
                msg='Your not eligible for plasma donoation!'
                return render_template('dashboard.html',msg=msg,donor_count=donor_count,request_count=request_count)
        ibm_db.execute(prep_stmt)
        return render_template('Request.html')

@app.route('/login',methods=['GET','POST'])
def login():
    global userid
    msg=''

    if request.method == 'POST':
        email=request.form['email']
        password=request.form['password']
        sql="SELECT * FROM DONORS WHERE EMAIL=? AND PASSWORD=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['loggedin'] = True
            session['id']=account['USERNAME']
            userid= account['USERNAME']
            session['USERNAME'] =account['USERNAME']
            msg = 'Logged in successfully!'

            return render_template('dashboard.html',msg=msg,donor_count=donor_count,request_count=request_count)
        else:
            msg='Incorrect username/password!'
    return render_template('login.html',msg=msg)

@app.route('/R_page',methods=['GET','POST'])
def R_page():
    return render_template('Register_1.html')

@app.route('/L_page',methods=['GET','POST'])
def L_page():
    return render_template('login.html')

@app.route('/Logout_page',methods=['GET','POST'])
def Logout_page():
    session['loggedin'] = False
    session['id']= ""
    userid= ""
    session['USERNAME'] = ""
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    global userid
    msg=''
    if request.method == 'POST':
        username= request.form['username']
        email=request.form['email']
        password= request.form['password']
        sql="SELECT * FROM DONORS WHERE USERNAME=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg= 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg='Invalid email'
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg='name must contain only alpha characters or numbers!'
        else:
            insert_sql="INSERT INTO DONORS(USERNAME,EMAIL,PASSWORD)VALUES(?,?,?)"
            prep_stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,username)
            ibm_db.bind_param(prep_stmt,2,email)
            ibm_db.bind_param(prep_stmt, 3,password)
            ibm_db.execute(prep_stmt)

            session['USERNAME'] =username
            msg='you have successfully registered!'
    elif request.method == 'POST':
        msg= "Please fill out the form"
    print(msg)
    return render_template( 'Register_2.html', msg=msg,userid=username)

@app.route('/secondregister',methods=['GET','POST'])
def secondregister():
    global userid
    msg=''
    if request.method == 'POST':
        address= request.form['address']
        phone=request.form['phone']
        blood_type= request.form['blood_type']
        userid= session['USERNAME']

        insert_sql="update DONORS set ADDRESS=?,MOBILE_NO=?,BLOOD_TYPE=? where USERNAME=?"
        prep_stmt=ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(prep_stmt,1,address)
        ibm_db.bind_param(prep_stmt,2,phone)
        ibm_db.bind_param(prep_stmt,3,blood_type)
        ibm_db.bind_param(prep_stmt,4,userid)
        ibm_db.execute(prep_stmt)
        msg='you have successfully registered!'
    else:
        msg= "Please fill out the form"
    print(msg)
    return render_template( 'login.html', msg=msg,donor_count=donor_count,request_count=request_count)

if __name__ == "__main__":
    app.run(host ='0.0.0.0',port = 5001, debug = True)