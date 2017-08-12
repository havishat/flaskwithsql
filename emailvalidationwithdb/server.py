from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
EMAILisnotvalid = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'KeepItSecretKeepItSafe'
mysql = MySQLConnector(app,'emailsdb')
@app.route('/')
def index():
    return render_template('index.html') # pass data to our template
@app.route('/success', methods=['POST'])
def create():
    email_entry = request.form['email']
    data = {
          'email': email_entry,
        }


    email_check = "SELECT * FROM emails WHERE email = :email"                           # define your query
    email_db = mysql.query_db(email_check,data)                           # run query with query_db()

    query = "INSERT INTO emails (email, created_at, updated_at) VALUES (:email, NOW(), NOW())"
    # We'll then create a dictionary of data from the POST data received.

    enter = mysql.query_db(query, data)

    query2 = "SELECT * FROM emails"
    allemails = mysql.query_db(query2)

    if not EMAILisnotvalid.match(request.form['email']):
      flash("Invalid Email Address!")
      return render_template('index.html')
    elif email_db:
      flash("Email already there")
    else:
      flash("The email address you entered " + request.form['email'] + "is a VALID email address! Thank you!")
      return render_template('success.html', all_emails=allemails)
    
    return redirect('/')
app.run(debug=True)
