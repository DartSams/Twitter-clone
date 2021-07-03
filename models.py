from threading import current_thread
import mysql.connector
from dotenv import load_dotenv
import os


load_dotenv()

db=mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Dartagnan19@",
    database="testdatabase"
    )

mycursor=db.cursor(buffered=True)

##select individual
# x=mycursor.execute("SELECT * FROM Discord_DB WHERE name = 'Enemy of my Enemy'")

# print(mycursor.fetchone()[0])

# lst=[]
# all=mycursor.execute('SELECT * FROM Post_Table')

# for i in mycursor:
#     print(i)
    # lst.append(i)

# print(lst)

# mycursor.execute("select * from Post_Table ORDER BY personID DESC LIMIT 1")
# mycursor.execute("select * from Post_Table ORDER BY personID DESC LIMIT 1")
# # mycursor.execute("UPDATE Post_Table SET post_img=%s WHERE ")

# for i in mycursor:
#     print(i)
#     id=i[4]
#     print(id)

#     mycursor.execute("UPDATE Post_Table SET post_img=%s WHERE personID=%s",('boobs',id))
#     db.commit()


def create_db(table_name):
    # mycursor.execute(f"CREATE TABLE {table_name} (name VARCHAR(100),username VARCHAR(100),password VARCHAR(100), email VARCHAR(100),privilege VARCHAR(100),gender VARCHAR(100),age INT,birthday VARCHAR(100),join_date VARCHAR(100), personID INT PRIMARY KEY AUTO_INCREMENT)")
    mycursor.execute(f"CREATE TABLE {table_name} (author VARCHAR(100),post_date VARCHAR(100),post VARCHAR(100),post_img VARCHAR(100),personID INT PRIMARY KEY AUTO_INCREMENT)")

# create_db('Twitter_Users')
# create_db('Post_Table')

def insert_user():
    # mycursor.execute("INSERT INTO Flask_Profile_Info (author,gender,age,job,location) VALUES (%s,%s%s,%s,%s)", ("iphone 69+","Dsams"))
    mycursor.execute("INSERT INTO Post_Table (author,post_date,post) VALUES (%s,%s,%s)", ("dartsams","Sat Jun 12 14:13:45 2021","i hate life"))
    db.commit()

# insert_user()


def show_entries(table_name):
    user=[]
    mycursor.execute(f"SELECT * FROM {table_name}")
    for i in mycursor:
        print(i)
        user.append(i)
        # return i
    # return [i for i  in mycursor]
    # print([i for i in mycursor])
    return user

# show_entries('Discord_db')

def delete_user(something):
    # mycursor.execute(f"DELETE FROM Discord_DB WHERE name='{name}' AND password='{password}'")
    # mycursor.execute(f"DELETE FROM Flask_Login WHERE name='{name}'")
    mycursor.execute(f"DELETE FROM Post_Table WHERE post_img='{something}'")

    db.commit()

# delete_user("None")

def update_data(password,math,new_value):
    mycursor.execute(f"UPDATE Discord_DB SET money = money {math} {new_value} WHERE password = '{password}'")
    db.commit()

# update_data('6047','+','999999')
# update_data('3979','+','999999')

# show_entries('Discord_DB')


def delete_db(table):
    mycursor.execute(f"DROP TABLE {table}")
    db.commit()

# delete_db('Twitter_Users')
# delete_db('Post_Table')


def add_column(table,column):
    mycursor.execute(f"ALTER TABLE {table} ADD {column} varchar(300)")

# add_column("Twitter_Users","profile_banner")
# add_column("Post_Table","post_img")


def get_columns(table):
    mycursor.execute("SHOW columns FROM Flask_Inventory")
    for i in mycursor:
        print(i[0])

def join_tables():
    mycursor.execute("SELECT * from Twitter_Users INNER JOIN Post_Table on name= author")
    for i in mycursor:
        print(i)

# join_tables()


import time
def show_entries(table_name):
    user=[]
    lst=[]
    post_date=time.ctime()
    print(post_date)
    all=mycursor.execute(f"SELECT * FROM {table_name}")

    # for i in mycursor:
        # split_date=i[1].split(" ")
        # print(i)
    #     lst.append(split_date[1])
    #     # current_date=split_date
    #     for index,item in enumerate(split_date[:]):
    #         if index % 2 == 0:
    #             lst.append(item)
    #             date=" "
    #             # date.join(item)
    #             # for im in lst:
    #             #     date.join(im)
    #             print(index,item)

    # date=date.join(lst)
    # print(date)


    ## return correct posted hours
    # for i in mycursor:
    #     # i[2]="hello"
    #     print(i)
        # lst.append(i)
        # print(i[1].split(" ")[3].split(":")[0].replace(i[1].split(" ")[3].split(":")[0],finished_post_time))
    split_date=post_date.split(" ")
    # print(split_date)
    split_hours=split_date[4].split(":")
    # print(split_hours)
    current_hour=int(split_hours[0])
    # print(current_hour)
    if current_hour >12:
        finished_post_time=current_hour-12
        # print(current_hour)
        # print(split_hours)
        if finished_post_time >0:
            # pass

            if current_hour >12:
                # print(str(finished_post_time) + ":" + str(split_hours[1]) + " pm")
                return "Posted " + str(finished_post_time) + ":" + str(split_hours[1]) + " pm"
            else:
                # print(str(finished_post_time) + ":" + str(split_hours[1]) + " am")
                return str(finished_post_time) + ":" + str(split_hours[1]) + " am"


            # i[1]=finished_post_time
            # print(i.split(' ').replace(i[1].split(" ")[3].split(":")[0],finished_post_time))


    elif current_hour <12:
        return str(current_hour) + ":" + str(split_hours[1]) + " am"
        # return str(finished_post_time) + ":" + str(split_hours[1]) + " am"
    


print(show_entries("Post_Table"))
# show_entries("Post_Table")

def replace( x, y): 
   mycursor.execute(f"SELECT * FROM Post_Table")
   for element in mycursor: 
      if element == x: 
         mycursor[element] = y 
   new_tuple = tuple(mycursor) 
   return new_tuple 

# replace(('michael', 'Sat Jun 19 00:29:52 2021', 'vdvfb'),"new time")