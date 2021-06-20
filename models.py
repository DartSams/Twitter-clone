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

lst=[]
all=mycursor.execute('SELECT * FROM Post_Table')

for i in mycursor:
    print(i)
    lst.append(i)

# print(lst)

def create_db(table_name):
    # mycursor.execute(f"CREATE TABLE {table_name} (name VARCHAR(100),password VARCHAR(100), email VARCHAR(100),privilege VARCHAR(100), personID int PRIMARY KEY AUTO_INCREMENT)")
    mycursor.execute(f"CREATE TABLE {table_name} (author VARCHAR(100),post_date VARCHAR(100),post VARCHAR(100))")

# create_db('Post_Table')

def insert_user():
    # mycursor.execute("INSERT INTO Flask_Profile_Info (author,gender,age,job,location) VALUES (%s,%s%s,%s,%s)", ("iphone 69+","Dsams"))
    mycursor.execute("INSERT INTO Post_Table (author,post_date,post) VALUES (%s,%s,%s)", ("dartsams","july 19,2021","i hate life"))
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

def delete_user(name,password):
    # mycursor.execute(f"DELETE FROM Discord_DB WHERE name='{name}' AND password='{password}'")
    # mycursor.execute(f"DELETE FROM Flask_Login WHERE name='{name}'")
    mycursor.execute(f"DELETE FROM Post_Table WHERE author='{name}'")

    db.commit()

# mycursor.execute(f"DELETE FROM Flask_Login")
# db.commit()
# delete_user('hello world','3977')
# delete_user('dartsams','3977')

def update_data(password,math,new_value):
    mycursor.execute(f"UPDATE Discord_DB SET money = money {math} {new_value} WHERE password = '{password}'")
    db.commit()

# update_data('6047','+','999999')
# update_data('3979','+','999999')

# show_entries('Discord_DB')


def delete_db(table):
    mycursor.execute(f"DROP TABLE {table}")
    db.commit()

# delete_db('Post_Table')


def show_balance(password):
    mycursor.execute(f"SELECT * FROM Discord_db WHERE password = '{password}'")
    result=mycursor.fetchall()

    for i in result:
        # print(i)
        return f"You have ${i[2]}"
# show_balance('3977')

def balance_check(password):
    mycursor.execute(f"SELECT * FROM Discord_db WHERE password = '{password}'")
    result=mycursor.fetchall()

    for i in result:

        if i[2] >=500:
            print('Welcome to the slots')
            return True

# balance_check('3977')


def add_column(table):
    mycursor.execute(f"ALTER TABLE {table} ADD ")


def get_columns(table):
    mycursor.execute("SHOW columns FROM Flask_Inventory")
    for i in mycursor:
        print(i[0])

def join_tables(table):
    mycursor.execute("SELECT * from Flask_Login INNER JOIN Flask_Inventory on name= author")
    for i in mycursor:
        print(i)