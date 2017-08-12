from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import sys
from datetime import datetime 
import md5 
# import os, binascii # include this at the top of your file
# salt = binascii.b2a_hex(os.urandom(15))
name = re.compile(r'^[^0-9]+$')
EMAILisnotvalid = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
passd = re.compile(r'^([^0-9]*|[^A-Z]*)$')

app = Flask(__name__)
app.secret_key = 'Login'
salt = "secure"
mysql = MySQLConnector(app,'registrationsdb')
#index route will handle rendering our form
@app.route('/')
def index(): 
  return render_template("index.html")

@app.route('/registration', methods=['POST']) 
def form():
  confirm_password = request.form['confirm_password']
  errors = False
  if len(request.form['first_name']) == 0 or len(request.form['last_name'])== 0 or len(request.form['email'])== 0 or len(request.form['password'])== 0 or len(request.form['confirm_password'])== 0 : 
    flash("Cannot be blank!")
    errors = True
  if len(request.form['first_name']) < 2 : 
    flash('First name must be at least two characters')
    errors = True
  if not request.form['first_name'].isalpha():
    flash('First name must be all letters')
    errors = True
  if not request.form['last_name'].isalpha():
    flash('Last name must be all letters')
    errors = True
  if len(request.form['last_name'])< 2 :
    flash('Last name must be at least two characters') 
    errors = True
  if not EMAILisnotvalid.match(request.form['email']):
    flash("Invalid Email Address!")
    errors = True
  if len(request.form['password']) < 8 :
    flash("Password should be more than 8 characters")
    errors = True
  if passd.match(request.form['password']):
    flash("least 1 uppercase letter and 1 numeric value")
    errors = True
  if request.form['password'] != confirm_password:
    flash("Password and Password Confirmation are not same")
    errors = True
  if errors:
    return redirect('/')
  else:
    hashed_pw = md5.new(salt+request.form['password']+salt).hexdigest()
    query = "INSERT INTO registration (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :pw, NOW(), NOW())"
    data = {
      "first_name": request.form["first_name"],
      "last_name": request.form["last_name"],
      "email": request.form["email"],
      "pw": hashed_pw
    }
    mysql.query_db(query, data)
    return redirect('/')

@app.route('/login', methods=['POST'])
def registrations():
  email = request.form['email']
  password = request.form['password']
  user_query = "SELECT  id, email, first_name, last_name, password FROM registration WHERE registration.email = :email"
  query_data = {'email': email}
  user = mysql.query_db(user_query, query_data)
  if len(user) != 0:
    encrypted_password = md5.new(salt+request.form['password']+salt).hexdigest()
    if user[0]['password'] == encrypted_password and user[0]['email'] == email:
      session['user_id'] = user[0]['id']
      session['user_name'] = user[0]['first_name'] + " " + user[0]['last_name']
      return redirect('/success')
      # this means we have a successful login!
    elif user[0]['password'] != encrypted_password :
      flash("password is wrong")
      return render_template('index.html')
        # invalid password   ` u!
    elif user[0]['email'] != email:
      flash("email id is worng")
      return render_template('index.html')
       # invalid email!
  # return redirect('/')

@app.route('/success')
def success():
	return render_template('success.html')

app.run(debug=True) # run our server
