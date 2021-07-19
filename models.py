from threading import current_thread
import mysql.connector
from dotenv import load_dotenv
import os
import time


load_dotenv()

db=mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Dartagnan19@",
    database="testdatabase"
    )

mycursor=db.cursor(buffered=True)

# mycursor.execute("select * from Post_Table")
# for i in mycursor:
#     print(i)
#     author=i[0]
#     date=i[1]
#     post_time=i[2]
#     post=i[3]
#     post_file=i[4]
#     placeholder_date=i[5]
#     id=i[6]
#     print(post,placeholder_date)




def create_db(table_name):
    # mycursor.execute(f"CREATE TABLE {table_name} (name VARCHAR(100),username VARCHAR(100),password VARCHAR(100), email VARCHAR(100),privilege VARCHAR(100),gender VARCHAR(100),age INT,birthday VARCHAR(100),join_date VARCHAR(100), personID INT PRIMARY KEY AUTO_INCREMENT)")
    mycursor.execute(f"CREATE TABLE {table_name} (author VARCHAR(100),post_date VARCHAR(100),post_time VARCHAR(100),post VARCHAR(100),post_file VARCHAR(100),placeholder_date VARCHAR(100),postID INT PRIMARY KEY AUTO_INCREMENT)")
    # mycursor.execute(f"CREATE TABLE {table_name} (author VARCHAR(100),post_date VARCHAR(100),post_time VARCHAR(100),comment VARCHAR(100),post_file VARCHAR(100),placeholder_date VARCHAR(100),commentID INT)")
    # mycursor.execute(f"CREATE TABLE {table_name} (name VARCHAR(100),id INT(100))")
# create_db('Twitter_Users')
# create_db('Post_Table')
# create_db("Comments")
# create_db("Likes")

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
    return user

# show_entries('Discord_db')

def delete_user(something):
    # mycursor.execute(f"DELETE FROM Flask_Login WHERE name='{name}'")
    mycursor.execute(f"DELETE FROM Post_Table WHERE post_img='{something}'")

    db.commit()

# delete_user("None")

def update_data(password,math,new_value):
    mycursor.execute(f"UPDATE Discord_DB SET money = money {math} {new_value} WHERE password = '{password}'")
    db.commit()

# update_data('6047','+','999999')
# update_data('3979','+','999999')

def delete_db(table):
    mycursor.execute(f"DROP TABLE {table}")
    db.commit()

# delete_db('Twitter_Users')
# delete_db('Post_Table')


def add_column(table,column):
    # mycursor.execute(f"ALTER TABLE {table} ADD {column} varchar(10)")
    mycursor.execute("ALTER TABLE Post_Table ADD like VARCHAR(10) NOT NULL")

# add_column("Twitter_Users","profile_banner")
# add_column("Post_Table","like")


def get_columns(table):
    mycursor.execute("SHOW columns FROM Flask_Inventory")
    for i in mycursor:
        print(i[0])

def join_tables():
    mycursor.execute("SELECT * from Twitter_Users INNER JOIN Post_Table on name= author")
    for i in mycursor:
        print(i)

# join_tables()



def calculate_post_time(table_name):
    user=[]
    lst=[]
    post_date=time.ctime()
    # print(post_date)
    mycursor.execute(f"SELECT * FROM {table_name}")

    split_date=post_date.split(" ")
    if "" in split_date:
        split_date.remove("")
    print(split_date)
    split_hours=split_date[3].split(":")
    print(split_hours)
    current_hour=int(split_hours[0])
    print(current_hour)
    if current_hour >12:
        finished_post_time=current_hour-12

        if finished_post_time >0:

            if current_hour >12:
                return "Posted " + str(finished_post_time) + ":" + str(split_hours[1]) + " pm"
            else:
                return str(finished_post_time) + ":" + str(split_hours[1]) + " am"

    elif current_hour == 12:
        return str(current_hour) + ":" + str(split_hours[1]) + " am"

    elif current_hour <12:
        return str(current_hour) + ":" + str(split_hours[1]) + " am"
    
# calculate_post_time("Post_Table")

# print(calculate_post_time("Post_Table"))
# calculate_post_time("Post_Table")



def split_compare_date(full_date):
    full_date=full_date.split(" ")
    # full_date.remove("")
    print(full_date)
    month=full_date[1]
    day=full_date[2]
    year=full_date[4]
    # print(full_date)
    split_date=[month,day,year]
    date=" "
    compare_date=date.join(split_date)
    print(compare_date.split(" "))
    return compare_date.split(" ")

# full_date="Tue Jan 6 12:11:51 2019"
# print(split_compare_date(full_date))




def split_current_date(current_post_date):
    current_post_date=current_post_date.split(" ")
    if "" in current_post_date:
        current_post_date.remove("")
    print(current_post_date)
    month=current_post_date[1]
    day=current_post_date[2]
    year=current_post_date[4]
    split_date=[month,day,year]
    date=" "
    current_post_date=date.join(split_date)
    # print(current_post_date)
    return current_post_date.split(" ")

# current_post_date=time.ctime()
# print(split_current_date(current_post_date))


month_dict={
    "Jan":1,
    "Feb":2,
    "Mar":3,
    "Apr":4,
    "May":5,
    "Jun":6,
    "Jul":7,
    "Aug":8
}




def get_post_date_or_time():
    lst=[]
    full_date="Tue Jul 1 12:11:51 2021"
    current_post_date=time.ctime()


    compare_date=split_compare_date(full_date)
    current_post_date=split_current_date(current_post_date)

    if compare_date[0] != current_post_date[0]:
        #if month is the same move on to days
        month_difference=month_dict[current_post_date[0]] - month_dict[compare_date[0]]
        # print(f"{month_difference} months ago")

        # return f"{difference} months ago"
        lst.append(month_difference)

    elif compare_date[0] == current_post_date[0]:
        month_difference=0
        lst.append(month_difference)

    if compare_date[1] != current_post_date[1]:
        #if day is the same move on to year
        day_difference=int(current_post_date[1])-int(compare_date[1])
        # print(f"{day_difference} days ago")
        
        # return f"{difference} days ago"
        lst.append(day_difference)

    elif compare_date[1] == current_post_date[1]:
        day_difference=0
        lst.append(day_difference)

    if compare_date[2] != current_post_date[2]:
        #if year is the same move on to time
        year_difference=int(current_post_date[2])-int(compare_date[2])
        # print(f"{year_difference} years ago")
        
        # return f"{difference} years ago"
        lst.append(year_difference)

    elif compare_date[2] == current_post_date[2]:
        year_difference=0
        lst.append(year_difference)

    return lst

# get_post_date_or_time()
# print(get_post_date_or_time())
# print("*" *10)
# if get_post_date_or_time()[2] ==0:
#     print("Same year") 

#     if get_post_date_or_time()[0] == 0:
#         print("same month")

#         if get_post_date_or_time()[1] == 0:
#             print("same day")
        
#         else:
#             print(f"{get_post_date_or_time()[1]} days ago")
#     else:
#         print(f"{get_post_date_or_time()[0]} months ago")

# else:
#     print(f"{get_post_date_or_time()[2]} years ago")


def get_time_ago():
    full_date="Tue Mar 1 12:11:51 2021"
    current_post_date=time.ctime()
    compare_date=split_compare_date(full_date)
    current_post_date=split_current_date(current_post_date)


    if compare_date[2] == current_post_date[2]:
        print("Same year")
        
        if compare_date[0] == current_post_date[0]:
            print("same month")

            if compare_date[1] == current_post_date[1]:
                print("same day")
            
            elif compare_date[1] != current_post_date[1]:
                # print(f"{get_post_date_or_time()[1]} days ago")
                day_difference=int(current_post_date[1])-int(compare_date[1])
                print(f"{day_difference} days ago")
                return f"{day_difference} days ago"

        elif compare_date[0] != current_post_date[0]:
            # print(f"{get_post_date_or_time()[0]} months ago")
            month_difference=month_dict[current_post_date[0]] - month_dict[compare_date[0]]
            print(f"{month_difference} months ago")
            return f"{month_difference} days ago"

    elif compare_date[2] != current_post_date[2]:
        # print(f"{get_post_date_or_time()[2]} years ago")
        year_difference=int(current_post_date[2])-int(compare_date[2])
        print(f"{year_difference} years ago")
        return f"{year_difference} days ago"

# get_time_ago()

post_date=time.ctime()


# split_compare_date(post_date)

def get_time_ago(date1):
    # print(date1)
    # return "hell hole"
    full_date="Tue Jul 1 12:11:51 2021"
    current_post_date=time.ctime()
    # compare_date=split_compare_date(date1)
    compare_date=date1.split(" ")
    current_post_date=split_current_date(current_post_date)


    if compare_date[2] == current_post_date[2]:
        print("Same year") 

        if compare_date[0] == current_post_date[0]:
            print("same month")

            if compare_date[1] == current_post_date[1]:
                print("same day")
            
            elif compare_date[1] != current_post_date[1]:
                # print(f"{get_post_date_or_time()[1]} days ago")
                day_difference=int(current_post_date[1])-int(compare_date[1])
                print(f"{day_difference} days ago")
                return f"{day_difference} days ago"

        elif compare_date[0] != current_post_date[0]:
            # print(f"{get_post_date_or_time()[0]} months ago")
            month_difference=month_dict[current_post_date[0]] - month_dict[compare_date[0]]
            print(f"{month_difference} months ago")
            return f"{month_difference} months ago"

    elif compare_date[2] != current_post_date[2]:
        # print(f"{get_post_date_or_time()[2]} years ago")
        year_difference=int(current_post_date[2])-int(compare_date[2])
        print(f"{year_difference} years ago")
        return f"{year_difference} years ago"

# lst=[]
# mycursor.execute("select * from Post_Table")
# for i in mycursor:
#     # print(i)
#     author=i[0]
#     date=i[1]
#     # print(date)
#     post_time=i[2]
#     post=i[3]
#     post_file=i[4]
#     placeholder_date=i[5]
#     id=i[6]
#     lst.append(date)


# for i in lst:
#     # print(i)
#     a=get_time_ago(i)
#     # # print(a)
#     mycursor.execute("UPDATE Post_Table SET placeholder_date = %s WHERE post_date = %s" ,(a,i))
#     db.commit()

# print("Winner | "*20)
# mycursor.execute("select * from Post_Table")
# for i in mycursor:
#     print(i)

# import json
# mycursor=db.cursor(buffered=True,dictionary=True)


# mycursor.execute(f"SELECT* FROM Twitter_Users WHERE username = 'dartsams'")

# for i in mycursor:
#     print(i)