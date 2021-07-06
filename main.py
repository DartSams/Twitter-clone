from re import search
from flask import Flask,render_template,redirect,request,flash,session
from flask_bcrypt import Bcrypt #encrypt passwords 
from flaskext.mysql import MySQL #allows flask and mysql connection
from werkzeug.utils import secure_filename #upload images
from dotenv import load_dotenv #to get env variables for db connection
import os
import time
from PIL import Image
load_dotenv()


dirname=os.path.dirname(__file__) + "\static\preview_img"
# print(dirname)
UPLOAD_FOLDER = dirname
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'jfif', 'mp3', 'mp4']


app=Flask(__name__)
bcrypt=Bcrypt(app) ##to encrypt passwd https://flask-bcrypt.readthedocs.io/en/latest/
app.config['SECRET_KEY'] = 'hello' #use session to save personal data to so user doesnt have to log in over and over
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
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
    split_hours=split_date[4].split(":")
    current_hour=int(split_hours[0])
    if current_hour >12:
        finished_post_time=current_hour-12
        # print(current_hour)
        # print(split_hours)
        if finished_post_time >0:
            if current_hour >12:
                # print(str(finished_post_time) + ":" + str(split_hours[1]) + " pm")
                return str(finished_post_time) + ":" + str(split_hours[1]) + " pm"
            else:
                # print(str(finished_post_time) + ":" + str(split_hours[1]) + " am")
                return str(finished_post_time) + ":" + str(split_hours[1]) + " am"

    elif current_hour == 12:
        return str(current_hour) + ":" + str(split_hours[1]) + " am"

    elif current_hour <12:
        return str(current_hour) + ":" + str(split_hours[1]) + " am"

def allowed_file(filename):
    # print(filename)
    # return '.' in filename and filename.split('.',)[1].lower() in ALLOWED_EXTENSIONS
    extension=filename.split(".")[1].lower()
    if "." in filename and extension in ALLOWED_EXTENSIONS:
        return True
    
    else:
        return False

@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="GET":
        lst.clear()
        all_post=mycursor.execute(f"SELECT * FROM Post_Table")

        for post_data in mycursor:
            # print(post_data)
            lst.append(post_data)

        print("\nUsers in Twitter_Users:")
        mycursor.execute(f"SELECT * FROM Twitter_Users")
        for i in mycursor:
            print(i)

        print("\nUsers in Post_Table:")
        mycursor.execute(f"SELECT * FROM Post_Table")
        for i in mycursor:
            print(i)

        return render_template("index.html",messages=lst[::-1],ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS)

    elif request.method=="POST":
        # print(request.form)
        post=request.form.get("post-field")
        search_bar=request.form.get("search")
        print(search_bar)
        file = request.files['file']
        print(file)
        post_date=time.ctime()

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            try:
                im = Image.open(fr"{dirname}\{filename}")
                newsize = (100,100)
                im1 = im.resize(newsize)
                im1.save(fr"{dirname}\{filename}")

            except:
                pass

            mycursor.execute("select * from Post_Table ORDER BY personID DESC LIMIT 1")
            for i in mycursor:
                # print(i)
                id=i[4]
                print(id)

                mycursor.execute("INSERT INTO Post_Table (author,post_date,post,post_img) VALUES (%s,%s,%s,%s)", (session["username"],calculate_post_time(post_date),post,filename))
                conn.commit()
            return redirect("/")

        elif "file" not in request.files :
            return redirect("/")

        mycursor.execute("INSERT INTO Post_Table (author,post_date,post) VALUES (%s,%s,%s)", (session["username"],calculate_post_time(post_date),post))
        conn.commit()
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
            mycursor.execute(f"SELECT * FROM Twitter_Users WHERE username = '{username}'")
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
                mycursor.execute(f"SELECT * FROM Twitter_Users where username = %s",(username))
                myresult = mycursor.fetchone()

                if myresult == None:
                    mycursor.execute("INSERT INTO Twitter_Users (name,username,password, email,privilege) VALUES (%s,%s,%s,%s,%s)", (name,username,hash_passwd,email,'user'))
                    # conn.commit()
                    return redirect("/register/page=2")

                elif myresult != None:
                    print('username already exists')
                    flash('Username Already Exists')
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

@app.route("/<username>")
def profile(username):
    user_post=[]
    profile_stuff=[]
    if "username" in session:
        if request.method=="GET":
            mycursor.execute(f'SELECT * FROM Post_Table WHERE author=%s',username)
            for i in mycursor:
                # print(i)
                user_post.append(i)

            mycursor.execute(f"SELECT * FROM Twitter_Users WHERE username = %s",username)
            for i in mycursor:
                # print(i)
                profile_stuff.append(i)
            
            if not user_post:
                flash("No Post Yet")
                
            files=os.listdir(dirname)
            print(files)
            # print(user_post)
            # print(profile_stuff)
            return render_template("profile.html",username=username,user_post=user_post[::-1],profile_stuff=profile_stuff,files=files,ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS)

    else:
        return redirect("/")

@app.route('/logout')
def logout():
    if "username" in session:
        session.pop("username")
        return redirect("/")
    
    else:
        return redirect("/")

@app.route("/clear/<int:post_id>")
def clear(post_id):
    lst.clear()
    mycursor.execute(f"DELETE FROM Post_Table WHERE personID=%s",(post_id))
    conn.commit()
    return redirect("/")

@app.route("/profile/<username>/settings",methods=["GET","POST"])
def profile_settings(username):
    user_post=[]
    profile_stuff=[]
    if request.method=="GET":
        mycursor.execute(f'SELECT * FROM Post_Table WHERE author=%s',username)
        for i in mycursor:
            # print(i)
            user_post.append(i)

        mycursor.execute(f"SELECT * FROM Twitter_Users WHERE username = %s",username)
        for i in mycursor:
            # print(i)
            profile_stuff.append(i)

        return render_template("settings.html",user_post=user_post[::-1],profile_stuff=profile_stuff)

    elif request.method=="POST":
        profile_description=request.form['profile_description']
        print(request.form)
        print(request.files)
        profile_banner=request.files["profile_banner"]
        profile_img=request.files["profile_img"]

        mycursor.execute("UPDATE Twitter_Users SET profile_description = %s WHERE username = %s" ,(profile_description,username))

        if profile_banner and allowed_file(profile_banner.filename):
            filename1 = secure_filename(profile_banner.filename)
            profile_banner.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))

            im = Image.open(fr"{dirname}\{filename1}")
            newsize = (600,200)
            im1 = im.resize(newsize)
            im1.save(fr"{dirname}\{filename1}")

            mycursor.execute("UPDATE Twitter_Users SET profile_description = %s,profile_banner = %s WHERE username = %s" ,(profile_description,filename1,username))




        if profile_img and allowed_file(profile_img.filename):
            filename2 = secure_filename(profile_img.filename)
            profile_img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

            im = Image.open(fr"{dirname}\{filename2}")
            newsize = (200,200)
            im1 = im.resize(newsize)
            im1.save(fr"{dirname}\{filename2}")

        

            mycursor.execute("UPDATE Twitter_Users SET profile_description = %s,profile_img = %s WHERE username = %s" ,(profile_description,filename2,username))
        conn.commit()
        return redirect(f"/{session['username']}")

@app.route("/<int:post_id>")
def post(post_id):
    user_post=[]
    mycursor.execute(f'SELECT * FROM Post_Table WHERE personID=%s',post_id)
    # mycursor.execute(f'SELECT * FROM Post_Table WHERE personID=%s AND author=%s',post_id,username)
    for i in mycursor:
        # print(i)
        user_post.append(i)

    return render_template("post.html",user_post=user_post,ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS)
    

if __name__=="__main__":
    app.run(debug=True)