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

conn= ibm_db.connect("DATABASE= ;HOSTNAME= ;PORT= ;SECURITY=SSL;SSLSeverCertificate=DigiCertGlobalRootCA.crt;UID= ;PWD= ",'','')

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = 'your abi key'
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    

sql ="select * from Count_Values"
stmt=ibm_db.exec_immediate(conn,sql)
ibm_db.fetch_row(stmt)

donor_count =ibm_db.result(stmt,0)
request_count = ibm_db.result(stmt,1)
userid =''

@app.route('/')
def home():
    return render_template('Request.html')

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
        return render_template('login.html',msg=msg)
