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

@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="GET":
        lst.clear()
        all_post=mycursor.execute(f"SELECT * FROM Post_Table")

        for post_data in mycursor:
            lst.append(post_data)

        return render_template("index.html",messages=lst[::-1])

    elif request.method=="POST":
        # print(request.form)
        post=request.form.get("post-field")
    
        post_date=time.ctime()
        mycursor.execute("INSERT INTO Post_Table (author,post_date,post) VALUES (%s,%s,%s)", (session["username"],post_date,post))
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

        return render_template("login.html")

    elif request.method=="POST":
        username = request.form['username']
        password = request.form['password']


        if username and password != "":
            mycursor.execute(f"SELECT * FROM Twitter_Users WHERE name = '{username}'")
            result=mycursor.fetchall()

            for i in result:
                passwd_check=bcrypt.check_password_hash(i[1], password)

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
            username=request.form['username']
            session["username"]=username
            email=request.form['email']
            password=request.form['password']
            compare_password=request.form['compare-password']
                
            hash_passwd = bcrypt.generate_password_hash(password).decode('utf-8')

            if password==compare_password:
                mycursor.execute(f"SELECT * FROM Twitter_Users where name = %s",(username))
                myresult = mycursor.fetchone()

                if myresult == None:
                    mycursor.execute("INSERT INTO Twitter_Users (name,password,email,privilege) VALUES (%s,%s,%s,%s)", (username,hash_passwd,email,'user'))
                    conn.commit()
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
            username=session["username"]
            gender=request.form['gender']
            age=request.form['age']
            job_role=request.form['job']
            location=request.form['location']

            if 'terms-of-service' in request.form:
                mycursor.execute("INSERT INTO Flask_Profile_Info (author,gender,age,job,location) VALUES (%s,%s,%s,%s,%s)", (username,gender,age,job_role,location))
                conn.commit()
                print(f"User created: {username}")
                return redirect('/')


@app.route("/profile")
def profile():
    if request.method=="GET":
        return render_template("profile.html")


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
    mycursor.execute(f"DELETE FROM Post_Table WHERE author='dartsams'")
    conn.commit()
    return redirect("/")


if __name__=="__main__":
    app.run(debug=True)