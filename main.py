from re import search
from flask import Flask,render_template,redirect,request,flash,session,url_for
from flask_bcrypt import Bcrypt #encrypt passwords 
from flaskext.mysql import MySQL #allows flask and mysql connection
from werkzeug.utils import secure_filename #upload images
from dotenv import load_dotenv #to get env variables for db connection
import os
import time
from PIL import Image
import json
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

month_dict={
    "Jan":1,
    "Feb":2,
    "Mar":3,
    "Apr":4,
    "May":5,
    "Jun":6,
    "Jul":7,
    "Aug":8,
    "Sep":9,
    "Oct":10,
    "Nov":11,
    "Dec":12
}

def calculate_post_time(post_date):
    # post_date=time.ctime()
    ## return correct posted hours
    split_date=post_date.split(" ")
    if "" in split_date:
        split_date.remove("")
    split_hours=split_date[3].split(":")
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

    elif current_hour == 12 or current_hour == 0:
        current_hour=12
        return str(current_hour) + ":" + str(split_hours[1]) + " am"

    elif current_hour <12:
        # print(str(current_hour) + ":" + str(split_hours[1]) + " am")
        return str(current_hour) + ":" + str(split_hours[1]) + " am"

def split_compare_date(full_date):
    # print(full_date)
    full_date=full_date.split(" ")
    if "" in full_date:
        full_date.remove("")

    month=full_date[1]
    day=full_date[2]
    year=full_date[4]
    # print(full_date)
    split_date=[month,day,year]
    date=" "
    compare_date=date.join(split_date)
    # print(compare_date)
    return compare_date

def split_current_date(current_post_date):
    current_post_date=current_post_date.split(" ")
    if "" in current_post_date:
        current_post_date.remove("")
    # print(post_date)
    month=current_post_date[1]
    day=current_post_date[2]
    year=current_post_date[4]
    split_date=[month,day,year]
    date=" "
    current_post_date=date.join(split_date)
    # print(current_post_date)
    return current_post_date.split(" ")

def get_time_ago(date1):
    full_date="Tue Jul 1 12:11:51 2021"
    current_post_date=time.ctime()
    # compare_date=split_compare_date(date1)
    compare_date=date1.split(" ")
    current_post_date=split_current_date(current_post_date)


    if compare_date[2] == current_post_date[2]:
        # print("Same year") 
        pass

        if compare_date[0] == current_post_date[0]:
            # print("same month")
            pass

            if compare_date[1] == current_post_date[1]:
                # print("same day")
                pass
    
            elif compare_date[1] != current_post_date[1]:
                # print(f"{get_post_date_or_time()[1]} days ago")
                day_difference=int(current_post_date[1])-int(compare_date[1])
                # print(f"{day_difference} days ago")
                return f"{day_difference} days ago"

        elif compare_date[0] != current_post_date[0]:
            # print(f"{get_post_date_or_time()[0]} months ago")
            month_difference=month_dict[current_post_date[0]] - month_dict[compare_date[0]]
            # print(f"{month_difference} months ago")
            return f"{month_difference} months ago"

    elif compare_date[2] != current_post_date[2]:
        # print(f"{get_post_date_or_time()[2]} years ago")
        year_difference=int(current_post_date[2])-int(compare_date[2])
        # print(f"{year_difference} years ago")
        return f"{year_difference} years ago"

def change_dates(table_name,date_lst):
    mycursor.execute("select * from Post_Table")
    for i in mycursor:
        # print(i)
        author=i[0]
        date=i[1]
        post_time=i[2]
        post=i[3]
        post_file=i[4]
        placeholder_date=i[5]
        id=i[6]
        date_lst.append(date)
        # print(date,post_time)

    for date in date_lst:
        mycursor.execute(f"UPDATE {table_name} SET placeholder_date = %s WHERE post_date = %s" ,(get_time_ago(date),date))
        conn.commit()

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
    date_lst=[]
    like_lst=[]
    like_lst_id=[]
    change_dates("Post_Table",date_lst)
    date_lst.clear()
    if request.method=="GET":
        lst.clear()
        post_date=time.ctime()
        # print(post_date)
        all_post=mycursor.execute(f"SELECT * FROM Post_Table")

        for post_data in mycursor:
            # print(post_data)
            lst.append(post_data)


        ##on the homepage tell if user liked the post but i need to get all post_id and feed it into this function
        mycursor.execute(f'SELECT * FROM Likes WHERE name = %s',session["username"])
        for i in mycursor:
            # print(i)
            like_lst.append(i)

        for i in like_lst:
            # print(i)
            like_lst_id.append(i[1])

        # print("\nUsers in Twitter_Users:")
        # mycursor.execute(f"SELECT * FROM Twitter_Users")
        # for i in mycursor:
        #     print(i)

        # print("\nUsers in Post_Table:")
        # mycursor.execute(f"SELECT * FROM Post_Table")
        # for i in mycursor:
        #     print(i)
        
        return render_template("index.html",messages=lst[::-1],ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS,post_date=split_compare_date(post_date),like_lst=like_lst,like_lst_id=like_lst_id)

    elif request.method=="POST":
        # print(request.form)
        post=request.form.get("post-field")
        
        # print(file)
        post_date=time.ctime()
        # print(post_date)

        if 'file' in request.files:
            file = request.files['file']
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

                mycursor.execute("select * from Post_Table ORDER BY postID DESC LIMIT 1")
                for i in mycursor:
                    # print(i)
                    id=i[4]
                    # print(id)

                    mycursor.execute("INSERT INTO Post_Table (author,post_date,post_time,post,post_file) VALUES (%s,%s,%s,%s,%s)", (session["username"],split_compare_date(post_date),calculate_post_time(post_date),post,filename))
                    conn.commit()
                return redirect("/")

            elif "file" not in request.files :
                return redirect("/")

            mycursor.execute("INSERT INTO Post_Table (author,post_date,post_time,post) VALUES (%s,%s,%s,%s)", (session["username"],split_compare_date(post_date),calculate_post_time(post_date),post))
            conn.commit()
            return redirect("/")
        # elif 'like' in request.form:
        #     print("cum")
        #     return redirect("/")

        else:
            print(request.form)
            if "enter-search" in request.form and "search-bar"=="":
                pass
            elif "search-bar" in request.form:
                search=request.form["search-bar"]
                print(search)
                return redirect(f"/{search}")

            elif "Like" in request.form:
                like=request.form["Like"]
                # print(like)
                mycursor.execute("INSERT INTO Likes (name,id) VALUES (%s,%s) ",(session["username"],like) )
                conn.commit()
                # mycursor.execute("SELECT * FROM Likes")
                # for i in mycursor:
                #     print(i)

            elif "UnLike" in request.form:
                unlike=request.form["UnLike"]
                mycursor.execute("DELETE FROM Likes WHERE id = %s AND name = %s",(unlike,session["username"]))
                conn.commit()

            elif "Reply" in request.form:
                reply=request.form["Reply"]
                return redirect(f"/{reply}")

            elif "Retweet" in request.form:
                retweet=request.form["Retweet"]
                # print(retweet)
                mycursor.execute("SELECT * FROM Post_Table WHERE postID = %s", retweet)
                for i in mycursor:
                    # print(i)
                    post=i[3]
                    file_=i[4]
                    # print(type(file_))
                if file_ is None:
                    # print("text")
                    mycursor.execute("INSERT INTO Post_Table (author,post_date,post_time,post) VALUES (%s,%s,%s,%s)", (session["username"],split_compare_date(post_date),calculate_post_time(post_date),post))
                    conn.commit()
                else:
                    # print("img")
                    mycursor.execute("INSERT INTO Post_Table (author,post_date,post_time,post,post_file) VALUES (%s,%s,%s,%s,%s)", (session["username"],split_compare_date(post_date),calculate_post_time(post_date),post,file_))
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

@app.route("/<username>",methods=["GET","POST"])
def profile(username):
    user_post=[]
    profile_stuff=[]
    post_date=time.ctime()
    like_lst=[]
    like_lst_id=[]
    # if "username" in session:
    if request.method=="GET":
        mycursor.execute(f'SELECT * FROM Post_Table WHERE author=%s',username)
        for i in mycursor:
            # print(i)
            user_post.append(i)
        


        mycursor.execute(f"SELECT * FROM Twitter_Users WHERE username = %s",username)
        for i in mycursor:
            # print(i)
            profile_stuff.append(i)

        mycursor.execute(f'SELECT * FROM Likes WHERE name = %s',session["username"])
        for i in mycursor:
            # print(i)
            like_lst.append(i)

        for i in like_lst:
            # print(i)
            like_lst_id.append(i[1])

        mycursor.execute(f"SELECT * FROM Following WHERE name = %s ",session["username"])
        following = "fg"
        for i in mycursor:
            print(i)
            # print(session["username"])

        mycursor.execute(f"SELECT * FROM Twitter_Users where username = %s",(username))
        myresult = mycursor.fetchone()

        if myresult == None:
            flash("This user does not exist")

        elif not user_post:
            flash("No post yet")

            
        files=os.listdir(dirname)
        # print(files)
        # print(user_post)
        # print(profile_stuff)
        return render_template("profile.html",username=username,user_post=user_post[::-1],profile_stuff=profile_stuff,files=files,ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS,post_date=split_compare_date(post_date),like_lst=like_lst,like_lst_id=like_lst_id,following=following)

    elif request.method == "POST":
        print(request.form)
        files=os.listdir(dirname)
        if "Follow" in request.form:
            follow=request.form["Follow"]
            mycursor.execute("INSERT INTO Following (name,following) VALUES (%s,%s)",(session["username"],follow))
            conn.commit()

        # return render_template("profile.html",username=username,user_post=user_post[::-1],profile_stuff=profile_stuff,files=files,ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS,post_date=split_compare_date(post_date),like_lst=like_lst,like_lst_id=like_lst_id)
        return redirect(f"/{username}/following")

@app.route("/<username>/<tab>")
def profile2(username,tab):
    user_post=[]
    profile_stuff=[]
    post_date=time.ctime()
    like_lst=[]
    like_lst_id=[]
    comment_lst=[]
    following=[]
    # if "username" in session:
    if request.method=="GET":    
        mycursor.execute(f"SELECT * FROM Twitter_Users WHERE username = %s",username)
        for i in mycursor:
            # print(i)
            profile_stuff.append(i)

        mycursor.execute(f'SELECT * FROM Likes WHERE name = %s',username)
        for post in mycursor:
            # print(post)
            like_lst.append(post)

        for id in like_lst:
            # print(i)
            post_id=id[1]
            mycursor.execute("SELECT * FROM Post_Table WHERE postID=%s",post_id)
            for j in mycursor:
                user_post.append(j)
        
        mycursor.execute("SELECT * FROM Comments")
        for j in mycursor:
            comment_lst.append(j)

        mycursor.execute(f"SELECT * FROM Following WHERE following = %s ",username)
        for j in mycursor:
            following.append(j[0])
        
        # for i in like_lst_id:
        #     mycursor.execute("SELECT * FROM Post_Table WHERE postID=%s",i)
        #     for j in mycursor:
        #         user_post.append(j)

        mycursor.execute(f"SELECT * FROM Twitter_Users where username = %s",(username))
        myresult = mycursor.fetchone()

        if myresult == None:
            flash("This user does not exist")

        elif tab != "Likes" or tab != "Replies":
            flash("Hmm...this page doesn’t exist. Try searching for something else.")

        files=os.listdir(dirname)
        # print(files)
        # print(user_post)
        # print(profile_stuff)
        # if tabs == "":
        return render_template("profile_tabs.html",profile_stuff=profile_stuff,ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS,
            post_date=split_compare_date(post_date),like_lst=like_lst,like_lst_id=like_lst_id,user_post=user_post[::-1],
            comment_lst=comment_lst[::-1],tab=tab,following=following)

   


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
    mycursor.execute(f"DELETE FROM Post_Table WHERE postID=%s",(post_id))
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
        # print(request.form)
        # print(request.files)
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

@app.route("/<int:post_id>",methods=["GET","POST"])
def post(post_id):
    user_post=[]
    comments=[]
    date_lst=[]
    like_lst=[]
    change_dates("Comments",date_lst)
    post_date=time.ctime()
    if request.method=="GET":
        mycursor.execute(f'SELECT * FROM Post_Table WHERE postID=%s',post_id)
        # mycursor.execute(f'SELECT * FROM Post_Table WHERE personID=%s AND author=%s',post_id,username)
        for i in mycursor:
            # print(i)
            user_post.append(i)

        mycursor.execute(f'SELECT * FROM Comments WHERE commentID=%s',post_id)
        for i in mycursor:
            comments.append(i)

        mycursor.execute(f'SELECT * FROM Likes WHERE id=%s AND name=%s',(post_id,session["username"]))
        for i in mycursor:
            print(i)
            like_lst.append(i)


        if not comments:
            flash("No comments yet")

        if like_lst:
            return render_template("post.html",user_post=user_post,ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS,post_date=split_compare_date(post_date),comments=comments[::-1],like_lst=like_lst[0])

        elif not like_lst:
            return render_template("post.html",user_post=user_post,ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS,post_date=split_compare_date(post_date),comments=comments[::-1])

    elif request.method=="POST":
        comment=request.form.get("comment-field")
        if 'file' in request.files:

            file = request.files['file']
            # print(file)

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

                # mycursor.execute("select * from Comments ORDER BY commentID DESC LIMIT 1")
                # for i in mycursor:
                #     print(i)
                #     id=i[4]
                #     # print(id)

                mycursor.execute("INSERT INTO Comments (author,post_date,post_time,comment,post_file,commentID) VALUES (%s,%s,%s,%s,%s,%s)", (session["username"],split_compare_date(post_date),calculate_post_time(post_date),comment,filename,post_id))
                conn.commit()
                return redirect(f"/{post_id}")

            elif "file" not in request.files :
                return redirect(f"/{post_id}")

            mycursor.execute("INSERT INTO Comments (author,post_date,post_time,comment,commentID) VALUES (%s,%s,%s,%s,%s)", (session["username"],split_compare_date(post_date),calculate_post_time(post_date),comment,post_id))
            conn.commit()
            return redirect(f"/{post_id}")
        
        else:
            print(request.form)
            if "Like" in request.form:
                like=request.form.get("Like")
                print(like)
                mycursor.execute("INSERT INTO Likes (name,id) VALUES (%s,%s) ",(session["username"],like) )
                conn.commit()
                mycursor.execute("SELECT * FROM Likes")
                for i in mycursor:
                    print(i)
                
            elif "UnLike" in request.form:
                unlike=request.form.get("UnLike")
                mycursor.execute("DELETE FROM Likes WHERE id = %s AND name = %s",(unlike,session["username"]))
                conn.commit()
            return redirect(f"/{post_id}")

@app.route("/test" ,methods=["get","post"])
def test():
    # user = {'firstname': "Finn", 'lastname': "The Human"}
    # conn=mysql.connect(dictionary=True)




    # x=mycursor.execute(f"SELECT* FROM Twitter_Users WHERE username = 'dartsams'")
    # rv = mycursor.fetchall()
    # json_data=[]
    # for result in rv:
    #     json_data.append(dict(result))
    # x= json.dumps(json_data)


    # cur = mysql.connection.cursor()
    # mycursor.execute('''SELECT * FROM Post_Table ''')
    # row_headers=[x[0] for x in mycursor.description] #this will extract row headers
    # rv = mycursor.fetchall()
    # json_data=[]
    # for result in rv:
    #     json_data.append(dict(zip(row_headers,result)))
    # x= json.dumps(json_data)
    if request.method == "GET":
        html_files=["index.html","login.html"]
        return render_template("test.html",html_files=html_files)

    # elif request.method == "POST":
    #     print(request.form)
    #     if 'download' in request.form:
    #         print("cum")
    #     elif 'watch' in request.form:
    #         print("puhh")   
    #     return redirect(url_for('test'))

@app.route("/switch/<username>")
def switch(username):
    session["username"]= username
    return redirect(f"/{username}")

if __name__=="__main__":
    app.run(debug=True)