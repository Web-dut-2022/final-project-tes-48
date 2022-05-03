import os
import requests
import pymysql
from flask import Flask, session, render_template, url_for, request, flash, redirect, abort,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
Session(app)




# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

HOSTNAME = "127.0.0.1"
PORT = "3306"
DATABASE = "books"
USERNAME = "root"
PASSWORD = "123456"
DATABASE_URL = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=UTF8MB4".\
    format(username=USERNAME, password=PASSWORD, host=HOSTNAME, port=PORT, db=DATABASE)

engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))



@app.route("/")
def index():
    return render_template("index.html")

@app.route('/more')
def more():
    return render_template("more.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        reg_username = request.form.get('username')
        reg_password = request.form.get('password')
        if len(reg_username) < 1 or reg_username is '':
            return render_template("reminder.html", message="username can't be empty.")

        query = db.execute("SELECT * FROM users WHERE username=:username", {"username": reg_username}).fetchone()
        if query is None:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": reg_username, "password":reg_password})
            db.commit()
            return render_template("reminder.html", message="successfully registered, please login", m=1)
        else:
            return render_template("reminder.html", message="that username already exists!")

    return render_template('register.html')



@app.route('/buy/<string:isbn>', methods=['GET', 'POST'])
def buy(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return render_template("reminder.html", message="no such book")

    if request.method == 'POST':
        username = session['username']
        if username is None:
            return render_template("reminder.html", message="The username does not exist, please register first!!")

        location = request.form.get('location')
        if len(location) < 1 or location is '':
            return render_template("reminder.html", message="location can't be empty.")

        db.execute("INSERT INTO information (username, isbn, location) VALUES (:username, :isbn, :location)",
                       {"username": username, "isbn": isbn, "location": location})
        db.commit()
        return render_template("reminder.html", message="Successful purchase!!")
    return render_template("buy.html",isbn=isbn, book=book)



@app.route('/search', methods=['GET', 'POST'])
def search():
    books=[]
    if request.method == "POST":
        searchType = request.form.get('searchType')
        searchContent = request.form.get('searchContent')
        books=db.execute("SELECT * FROM books WHERE {searchType} LIKE '%{searchContent}%'".format(searchType=searchType, searchContent=searchContent)).fetchall()

    return render_template("search.html", books=books)

@app.route("/search/<string:isbn>",methods=['GET', 'POST'])
def book(isbn):
# Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return render_template("reminder.html", message="The username does not exist, please register first!!")
    reviews=[]
    if request.method == "POST" :
        username=session['username']
        if username is None:
            return render_template("reminder.html", message="The username does not exist, please register first!!")
        rank = request.form.get('rank')
        review = request.form.get('review')
        u=db.execute("SELECT * FROM reviews WHERE username = :username and isbn = :isbn", {"username": username , "isbn": isbn}).fetchone()
        if u is not None:
            return render_template("reminder.html", message="Sorry, each person can only comment once...")
        db.execute("INSERT INTO reviews (username, isbn, star, review) VALUES (:username, :isbn, :star,:review)", {"username": username, "isbn":isbn, "star":rank,"review":review})
        db.commit()

    # Get all reviews.
    reviews = db.execute("SELECT username,star,review FROM reviews WHERE isbn = :isbn",
                            {"isbn": isbn}).fetchall()
    return render_template("book.html", isbn=isbn, reviews=reviews, book=book)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        log_username = request.form.get('username')
        log_password = request.form.get('password')
        if len(log_username) < 1 or log_username is '':
            return render_template("reminder.html", message="username can not be empty.")

        query = db.execute("SELECT * FROM users WHERE username=:username", {"username": log_username}).fetchone()
        if query is None:
            return render_template("reminder.html", message="The user name does not exist, please register first")

        elif query is not None and query["password"] == log_password:
            session['username'] = log_username
            return render_template("reminder.html", message="Login successfully, and you can buy some books now!!", m=2)

        elif query is not None and query["password"] != log_password:
            return render_template("reminder.html", message="Sorry,wrong password...")

    return render_template('login.html')

@app.route('/Exactly', methods=['GET', 'POST'])
def Exactly():
    if request.method == "POST":
        Gisbn = request.form.get('isbn')
    if len(Gisbn) < 1 or Gisbn is '':
        return render_template("reminder.html", message="isbn can not be empty.")

    b = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": Gisbn}).fetchone()
    if b is None:
        return render_template('reminder.html', message="No books,please retry!")
    else:
        count = db.execute("SELECT DISTINCT COUNT(*) co FROM books WHERE isbn =:isbn", {"isbn": Gisbn}).fetchone()
        r = db.execute("SELECT * FROM reviews WHERE isbn =:isbn", {"isbn": Gisbn}).fetchone()
        return render_template('Exactly.html', book=b, count=count, Reviews=r)
    return render_template('Exactly.html')

    return render_template('Eactly.html')

@app.route('/show/<string:username>')
def show(username):
    n=[]
    books=[]
    n = db.execute("SELECT * FROM information WHERE username =:username", {"username": username}).fetchone()
    if n is None:
        return render_template('reminder.html', message="No user,please retry!")
    isbn=n.isbn
    books=db.execute("SELECT DISTINCT * FROM books where isbn =:isbn", {"isbn": isbn}).fetchone()
    return render_template('show.html', information=n, book=books)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == "POST":
        disbn = request.form.get('isbn')
        if len(disbn) < 1 or disbn is '':
            return render_template("reminder.html", message="isbn can not be empty.")

        query = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": disbn}).fetchone()
        if query is None:
            return render_template('reminder.html', message="No this isbn,please retry!")

        else:
            db.execute("DELETE FROM books WHERE isbn=:isbn ",
                       {"isbn": disbn})
            db.execute("DELETE FROM reviews WHERE isbn=:isbn ",
                       {"isbn": disbn})
            db.execute("DELETE FROM information WHERE isbn=:isbn ",
                       {"isbn": disbn})
            db.commit()
            return render_template('reminder.html', message="Successfully delete!")

        return render_template('delete.html')

    return render_template('delete.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        aisbn = request.form.get('isbn')
        atitle = request.form.get('title')
        aauthor = request.form.get('author')
        amoney = request.form.get('money')
        if len(aisbn) < 1 or aisbn is '':
            return render_template("reminder.html", message="isbn can not be empty.")
        if len(atitle) < 1 or aisbn is '':
            return render_template("reminder.html", message="title can not be empty.")
        if len(aauthor) < 1 or aisbn is '':
            return render_template("reminder.html", message="author can not be empty.")
        if len(amoney) < 1 or aisbn is '':
            return render_template("reminder.html", message="money can not be empty.")

        query = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": aisbn}).fetchone()
        if query is None:
            db.execute("INSERT INTO books (isbn, title, author, money) VALUES (:isbn, :title, :author, :money)",
                       {"isbn": aisbn, "title": atitle, "author":aauthor, "money": amoney})
            db.commit()
            return render_template("reminder.html", message="successfully add book")
        else:
            return render_template("reminder.html", message="that book already exists!")

    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)