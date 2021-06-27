from flask import Flask,render_template,redirect,request,flash,session
from flask_bcrypt import Bcrypt #encrypt passwords 
from flaskext.mysql import MySQL #allows flask and mysql connection
from dotenv import load_dotenv #to get env variables for db connection
import os
import time
load_dotenv()

app=Flask(__name__)
bcrypt=Bcrypt(app) ##to encrypt passwd https://flask-bcrypt.readthedocs.io/en/latest/
app.config['SECRET_KEY'] = 'hello' #use session to save personal data to so user doesnt have to log in over and over
mysql=MySQL() #to connect flask to mysql


app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=os.getenv('password')
app.config['MYSQL_DATABASE_DB']='testdatabase'
mysql.init_app(app)

conn=mysql.connect()
mycursor=conn.cursor()

lst=[]

def calculate_post_time(post_date):
    post_date=time.ctime()
    print(post_date)

    ## return correct posted hours
    split_date=post_date.split(" ")
    split_hours=split_date[3].split(":")
    current_hour=int(split_hours[0])
    if current_hour >12:
        finished_post_time=current_hour-12
        # print(current_hour)
        # print(split_hours)
        if finished_post_time >0:
            if current_hour >12:
                # print(str(finished_post_time) + ":" + str(split_hours[1]) + " pm")
                return "Posted " + str(finished_post_time) + ":" + str(split_hours[1]) + " pm"
            else:
                # print(str(finished_post_time) + ":" + str(split_hours[1]) + " am")
                return str(finished_post_time) + ":" + str(split_hours[1]) + " am"

@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="GET":
        lst.clear()
        all_post=mycursor.execute(f"SELECT * FROM Post_Table")

        for post_data in mycursor:
            # print()
            lst.append(post_data)

        print("\nUsers in Twitter_Users:")
        mycursor.execute(f"SELECT * FROM Twitter_Users")
        for i in mycursor:
            print(i)

        print("\nUsers in Post_Table:")
        mycursor.execute(f"SELECT * FROM Post_Table")
        for i in mycursor:
            print(i)

        return render_template("index.html",messages=lst[::-1])

    elif request.method=="POST":
        # print(request.form)
        post=request.form.get("post-field")
        post_date=time.ctime()


        mycursor.execute("INSERT INTO Post_Table (author,post_date,post) VALUES (%s,%s,%s)", (session["username"],calculate_post_time(post_date),post))
        conn.commit()
        # file=request.files["file"]
        # if "file" not in request.files or file.filename == "":

        return redirect("/")
            

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="GET":
        username=""
        password=""
        
        print("\nUsers in Twitter_Users:")
        mycursor.execute(f"SELECT * FROM Twitter_Users")
        for i in mycursor:
            print(i)

        print("\nUsers in Post_Table:")
        mycursor.execute(f"SELECT * FROM Post_Table")
        for i in mycursor:
            print(i)

        return render_template("login.html")

    elif request.method=="POST":
        username = request.form['username']
        password = request.form['password']


        if username and password != "":
            mycursor.execute(f"SELECT * FROM Twitter_Users WHERE name = '{username}'")
            result=mycursor.fetchall()

            for i in result:
                passwd_check=bcrypt.check_password_hash(i[2], password)

            if passwd_check == True:
                session["username"]=username
                return redirect(f'/')     
            
            elif passwd_check == False:
                return redirect('/login')

        elif username and password == "" or username == "" or password == "":
            print('You must fill in the username and password fields')
            flash("You must fill in the username and password fields")
            return redirect('/login')


@app.route("//register/page=<int:page_id>",methods=["GET","POST"])
def create_account(page_id):
    if page_id==1:
        if request.method=="GET":
            return render_template("register.html")
        
        elif request.method=="POST":
            name=request.form["name"]
            username=request.form['username']
            session["username"]=username
            email=request.form['email']
            password=request.form['password']
            compare_password=request.form['compare-password']
            post_date=time.ctime()
                
            hash_passwd = bcrypt.generate_password_hash(password).decode('utf-8')

            if password==compare_password:
                mycursor.execute(f"SELECT * FROM Twitter_Users where name = %s",(username))
                myresult = mycursor.fetchone()

                if myresult == None:
# name,username,password, email,privilege,birthday,join_date
                    mycursor.execute("INSERT INTO Twitter_Users (name,username,password, email,privilege) VALUES (%s,%s,%s,%s,%s)", (name,username,hash_passwd,email,'user'))
                    # conn.commit()
                    return redirect("/register/page=2")

                elif myresult != None:
                    print('username already exists')
                    return redirect("/register/page=1")
                    
            
            else:
                return redirect('/register/page=1')


    elif page_id==2:
        if request.method=="GET":
            return render_template("register2.html")

        elif request.method=="POST":
            # name=request.form["name"]
            username=session["username"]
            gender=request.form['gender']
            age=request.form['age']
            # job_role=request.form['job']
            # location=request.form['location']
            birthday=request.form['birthday']
            join_date=time.ctime()

            if 'terms-of-service' in request.form:
                mycursor.execute("UPDATE Twitter_Users SET gender = %s,age = %s,birthday = %s, join_date = %s WHERE username = %s" ,(gender,age,birthday,join_date,session["username"]))
                # mycursor.execute("INSERT INTO Twitter_Users (name,username,password,email,privilege,gender,age,location,birthday,join_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (name,username,password,email,privilege,gender,age,location,birthday,join_date))
                conn.commit()
                print(f"User created: {username}")
                return redirect('/')


@app.route("/profile")
def profile():
    user_post=[]
    if "username" in session:
        if request.method=="GET":
            mycursor.execute(f'SELECT * FROM Post_Table WHERE author=%s',(session["username"]))
            for i in mycursor:
                print(i)
                user_post.append(i)
            
            if not user_post:
                flash("No Post Yet")
                
            return render_template("profile.html",user_post=user_post[::-1])

    else:
        return redirect("/")


@app.route('/logout')
def logout():
    if "username" in session:
        session.pop("username")
        return redirect("/")
    
    else:
        return redirect("/")

@app.route("/clear")
def clear():
    lst.clear()
    mycursor.execute(f"DELETE FROM Post_Table WHERE author=%s",(session["username"]))
    conn.commit()
    return redirect("/")


if __name__=="__main__":
    app.run(debug=True)