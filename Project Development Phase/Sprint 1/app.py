from flask import Flask,render_template,request,redirect,url_for,session
import ibm_db
import re

app=Flask(__name__)

app.secret_key='a'

conn= ibm_db.connect("DATABASE= ;HOSTNAME= ;PORT= ;SECURITY=SSL;SSLSeverCertificate=DigiCertGlobalRootCA.crt;UID= ;PWD= ",'','')

@app.route('/')
def home():
    return render_template('Register_1.html')

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

            return "sucesss"
        else:
            msg='Incorrect username/password!'
    return render_template('login.html',msg=msg)

@app.route('/R_page',methods=['GET','POST'])
def R_page():
    return render_template('Register_1.html')

@app.route('/L_page',methods=['GET','POST'])
def L_page():
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
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
            msg='you have successfully registered!'
    elif request.method == 'POST':
        msg= "Please fill out the form"
    print(msg)
    return render_template( 'Register_2.html', msg=msg)

@app.route('/secondregister',methods=['GET','POST'])
def secondregister():
    msg=''
    if request.method == 'POST':
        address= request.form['address']
        phone=request.form['phone']
        blood_type= request.form['blood_type']

        insert_sql="update DONORS set ADDRESS=?,MOBILE_NO=?,BLOOD_TYPE=?"
        prep_stmt=ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(prep_stmt,1,address)
        ibm_db.bind_param(prep_stmt,2,phone)
        ibm_db.bind_param(prep_stmt,3,blood_type)
        ibm_db.execute(prep_stmt)
        msg='you have successfully registered!'
    elif request.method == 'POST':
        msg= "Please fill out the form"
    print(msg)
    return "success"
