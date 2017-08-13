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
app.secret_key = 'wall'
salt = "secure"
mysql = MySQLConnector(app,'thewalldb')
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
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :pw, NOW(), NOW())"
    data = {
      "first_name": request.form["first_name"],
      "last_name": request.form["last_name"],
      "email": request.form["email"],
      "pw": hashed_pw
    }
    mysql.query_db(query, data)
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
  email = request.form['email']
  password = request.form['password']
  user_query = "SELECT  id, email, first_name, last_name, password FROM users WHERE users.email = :email"
  query_data = {'email': email}
  user = mysql.query_db(user_query, query_data)
  if len(user) != 0:
    encrypted_password = md5.new(salt+request.form['password']+salt).hexdigest()
    if user[0]['password'] == encrypted_password and user[0]['email'] == email:
      session['user_id'] = user[0]['id']
      session['user_name'] = user[0]['first_name'] + " " + user[0]['last_name']
      return redirect('/wall')
      # this means we have a successful login!
    elif user[0]['password'] != encrypted_password :
      flash("Your password is incorrect")
      return redirect('/')
        # invalid password!
    elif user[0]['email'] != email:
      flash("Your email is incorrect")
      return redirect('/')
       # invalid email!
    else: 
      flash("Your password and email is incorrect")
      return redirect('/')

@app.route('/messages', methods=['POST'])
def message():
  user_message = request.form['user_message']
  print user_message
  query_message = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES(:user_id, :message, NOW(), NOW())"
  data = {
    "user_id": session["user_id"],
    "message": user_message
	}
  mysql.query_db(query_message, data)
  return redirect('/wall')

@app.route('/comments/<message_id>', methods=['POST'])
def comment(message_id):
  user_comment = request.form['comment']
  query_comment = "INSERT INTO comments (user_id, message_id, comment, created_at, updated_at) VALUES(:user_id, :message_id, :comment, NOW(), NOW())"
  data = {
    "user_id": session["user_id"],
    "message_id": message_id,
    "comment": user_comment
	}
  mysql.query_db(query_comment, data)
  return redirect('/wall')

@app.route('/wall')
def success():
  query = "SELECT users.first_name, users.last_name, DATE_FORMAT(messages.created_at, '%M-%D %Y') as created_at, messages.message, messages.id FROM messages JOIN users ON messages.user_id = users.id"
  all_messages = mysql.query_db(query)
  # print all_messages
  for message in all_messages:
    message['comments'] =  []
    query1 = "SELECT users.first_name, users.last_name, DATE_FORMAT(comments.created_at, '%M-%D %Y') as created_at, comments.comment, comments.id FROM comments JOIN users ON comments.user_id = users.id WHERE comments.message_id = :message_id"
    data = {
      "message_id": message['id']
    }
    message['comments'] = mysql.query_db(query1, data)
  return render_template('thewall.html', messages = all_messages)

app.run(debug=True) # run our server
