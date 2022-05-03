import os
import csv
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

HOSTNAME = "127.0.0.1"
PORT = "3306"
DATABASE = "books"
USERNAME = "root"
PASSWORD = "123456"
DATABASE_URL = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=UTF8MB4".\
    format(username=USERNAME, password=PASSWORD, host=HOSTNAME, port=PORT, db=DATABASE)

engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("reviews.csv")
    reader = csv.reader(f)
    for username, isbn, star, review in reader:
        db.execute("INSERT INTO reviews (username, isbn, star, review) VALUES (:username, :isbn, :star, :review)",
                    {"username": username, "isbn": isbn, "star": star, "review": review})
        # print(f"Added {isbn}")
    db.commit()

    t = open("information.csv")
    reader = csv.reader(t)
    for username, isbn, location in reader:
        db.execute("INSERT INTO information (username, isbn, location) VALUES (:username, :isbn, :location)",
                   {"username": username, "isbn": isbn, "location": location})
        # print(f"Added {isbn}")
    db.commit()

    u = open("users.csv")
    reader = csv.reader(u)
    for username, password in reader:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                   {"username": username, "password": password})
        # print(f"Added {isbn}")
    db.commit()

    g = open("books.csv")
    reader = csv.reader(g)
    for isbn, title, author, money in reader:
        db.execute("INSERT INTO books (isbn, title, author, money) VALUES (:isbn, :title, :author, :money)",
                   {"isbn": isbn, "title": title, "author": author, "money":money})
        # print(f"Added {isbn}")
    db.commit()

if __name__ == '__main__':
    main()
