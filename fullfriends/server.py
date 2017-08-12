from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,'fullfriendsdb')
@app.route('/')
def index():
    query = "SELECT * FROM fullfriends"    
    query1 = "SELECT DATE_FORMAT(created_at, '%Y') FROM fullfriends"                    # define your query
    friends = mysql.query_db(query)                     # run query with query_db()
    return render_template('index.html', all_friends=friends) # pass data to our template
    # return render_template('index.html')
@app.route('/friends', methods=['POST'])
def create():
    # Write query as a string. Notice how we have multiple values
    # we want to insert into our query.
    query = "INSERT INTO fullfriends (Name, Age, created_at, updated_at) VALUES (:Name, :Age, NOW(), NOW())"
    # We'll then create a dictionary of data from the POST data received.
    data = {
             'Name': request.form['Name'],
             'Age': request.form['Age']
           }
    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)
    return redirect('/')
app.run(debug=True)
