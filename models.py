import mysql.connector
from dotenv import load_dotenv
import os
import time


load_dotenv()

db=mysql.connector.connect(
    host="localhost",
    user="dartsams",
    passwd="Dartagnan19@",
    database="Twitter"
    )

mycursor=db.cursor(buffered=True)


def create_db(db_name):
    mycursor.execute(f"CREATE DATABASE {db_name}")

# create_db("Twitter")


def create_table(table_name):
    # mycursor.execute(f"CREATE TABLE {table_name} (name VARCHAR(100),username VARCHAR(100),password VARCHAR(100), email VARCHAR(100),privilege VARCHAR(100),gender VARCHAR(100),age INT,birthday VARCHAR(100),join_date VARCHAR(100), personID INT PRIMARY KEY AUTO_INCREMENT,profile_description VARCHAR(100),profile_banner VARCHAR(100),profile_img VARCHAR(100))")
    # mycursor.execute(f"CREATE TABLE {table_name} (author VARCHAR(100),post_date VARCHAR(100),post_time VARCHAR(100),post VARCHAR(100),post_file VARCHAR(100),placeholder_date VARCHAR(100),postID INT PRIMARY KEY AUTO_INCREMENT)")
    # mycursor.execute(f"CREATE TABLE {table_name} (author VARCHAR(100),post_date VARCHAR(100),post_time VARCHAR(100),comment VARCHAR(100),post_file VARCHAR(100),placeholder_date VARCHAR(100),commentID INT)")
    # mycursor.execute(f"CREATE TABLE {table_name} (name VARCHAR(100),id INT(100))")
    # mycursor.execute(f"CREATE TABLE {table_name} (name VARCHAR(100),follower VARCHAR(100))")
    mycursor.execute(f"CREATE TABLE {table_name} (reported_by VARCHAR(100),postID INT(100))")

# create_table('Twitter_Users')
# create_table('Post_Table')
# create_table("Comments")
# create_table("Likes")
# create_table("Follow")
# create_table("Repost_Post")

def insert_user():
    # mycursor.execute("INSERT INTO Twitter_Users (name,username,password, email,privilege,gender,age,birthday,join_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (name,username,hash_passwd,email,'user',gender,age,birthday,join_date))
    db.commit()

# insert_user()


def show_entries(table_name):
    mycursor.execute(f"SELECT * FROM {table_name}")
    all_users=mycursor.fetchall()
    print(all_users)

# show_entries('Twitter_Users')
# show_entries('Post_Table')
# show_entries("Repost_Post")

def delete_user(data):
    # mycursor.execute(f"DELETE FROM Flask_Login WHERE username='{data}'")
    db.commit()

# delete_user("dartsams")

def update_data():
    #change to admin
    mycursor.execute("UPDATE Twitter_Users SET privilege = %s WHERE privilege = %s",("admin","user"))
    #change to user
    # mycursor.execute("UPDATE Twitter_Users SET privilege = %s WHERE privilege = %s",("user","admin"))
    db.commit()

# update_data()

def delete_db(table):
    mycursor.execute(f"DROP TABLE {table}")
    db.commit()
    print(f"Deleted '{table}' table")

# delete_db('Twitter_Users')
# delete_db('Post_Table')
# delete_db("Followers")
# delete_db("Comments")


def add_column(table,column):
    mycursor.execute(f"ALTER TABLE {table} ADD {column} VARCHAR(10) NOT NULL")

# add_column("Post_Table","like")


def get_columns(table):
    mycursor.execute(f"SELECT * FROM {table} ")
    row_headers=[x[0] for x in mycursor.description] #this will extract row headers
    return row_headers

# get_columns("Twitter_Users")

def join_tables():
    mycursor.execute("SELECT * from Twitter_Users INNER JOIN Post_Table on name= author")
    for i in mycursor:
        print(i)

# join_tables()