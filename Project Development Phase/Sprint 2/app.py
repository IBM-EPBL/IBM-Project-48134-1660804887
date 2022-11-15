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

conn= ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLSeverCertificate=DigiCertGlobalRootCA.crt;UID=lwj62946;PWD=hE2LCZgTYX3Iln9H",'','')

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
    return render_template('dashboard.html')

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
