from re import M
from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_bcrypt import Bcrypt  # encrypt passwords
from flaskext.mysql import MySQL  # allows flask and mysql connection
from werkzeug.utils import secure_filename  # upload images
from dotenv import load_dotenv  # to get env variables for db connection
import os
import time  # return current date & time
from PIL import Image  # save & edit images
import json
from flask_socketio import (
    SocketIO,
    emit,
    send,
    join_room,
    leave_room,
)  # replaces post requests

load_dotenv()


DIRNAME = os.path.dirname(__file__) + "\static\preview_img"
# print(dirname)
UPLOAD_FOLDER = DIRNAME
ALLOWED_EXTENSIONS = [
    "txt",
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "jfif",
]  # defining what type users can upload


app = Flask(__name__)  # init the flask ap
bcrypt = Bcrypt(app)  ##to encrypt passwd https://flask-bcrypt.readthedocs.io/en/latest/
app.config["SECRET_KEY"] = "hello"  # use session to save personal data to so user doesnt have to log in over and over
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

mysql = MySQL()  # to connect flask to mysql
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "dartsams"
app.config["MYSQL_DATABASE_PASSWORD"] = os.environ.get("password")
app.config["MYSQL_DATABASE_DB"] = "Twitter"
mysql.init_app(app)  # init the flask  to mysql connection

socketio = SocketIO(app)  # init the socket connection

# defines all months names and sets a numeric value
month_dict = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

## returns what time a post was made
def calculate_post_time(post_date):
    post_date = time.ctime()

    split_date = post_date.split(" ")
    if "" in split_date:  # this is for single digit days like 5,6,7 are different than 10,12,13
        split_date.remove("")
    split_hours = split_date[3].split(":")
    current_hour = int(split_hours[0])
    current_hour-=4 #this is because heroku servers arent located on the west coast so the if not this then servers return their time zone
    # print(current_hour)
    if current_hour > 12:
        finished_post_time = current_hour - 12
        # print(current_hour)
        # print(split_hours)
        if finished_post_time > 0:
            if current_hour > 12:
                # print(str(finished_post_time) + ":" + str(split_hours[1]) + " pm")
                return str(finished_post_time) + ":" + str(split_hours[1]) + " pm"
            else:
                # print(str(finished_post_time) + ":" + str(split_hours[1]) + " am")
                return str(finished_post_time) + ":" + str(split_hours[1]) + " am"

    elif current_hour == 12:
        current_hour = 12
        return str(current_hour) + ":" + str(split_hours[1]) + " pm"

    elif current_hour == 0:
        current_hour = 12
        return str(current_hour) + ":" + str(split_hours[1]) + " am"

    elif current_hour < 12:
        # print(str(current_hour) + ":" + str(split_hours[1]) + " am")
        return str(current_hour) + ":" + str(split_hours[1]) + " am"


# takes the time object and returns the original post day because the time object return day and time Ex. Sun Aug 15 20:28:12 2021
def split_compare_date(full_date):
    # print(full_date)
    full_date = full_date.split(" ")

    if (
        "" in full_date
    ):  # this is for single digit days like 5,6,7 are different than 10,12,13
        full_date.remove("")

    month = full_date[1]
    day = full_date[2]
    year = full_date[4]
    # print(full_date)
    split_date = [month, day, year]
    date = " "
    compare_date = date.join(split_date)
    # print(compare_date)
    return compare_date


# returns current day and splits it into a list
def split_current_date(current_post_date):
    current_post_date = current_post_date.split(" ")
    if "" in current_post_date:
        current_post_date.remove("")
    # print(post_date)
    month = current_post_date[1]
    day = current_post_date[2]
    year = current_post_date[4]
    split_date = [month, day, year]
    date = " "
    current_post_date = date.join(split_date)
    # print(current_post_date)
    return current_post_date.split(" ")


# compares the original date and the current post dates and returns how long ago it was posted Ex. 2 months ago
def get_time_ago(date1):
    # print(date1)
    full_date = "Tue Jul 1 12:11:51 2021"
    current_post_date = time.ctime()
    compare_date = date1.split(" ")
    # print(compare_date)
    current_post_date = split_current_date(current_post_date)
    # print(current_post_date)

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
                day_difference = int(current_post_date[1]) - int(compare_date[1])
                # print(f"{day_difference} days ago")
                return f"{day_difference} days ago"

        elif compare_date[0] != current_post_date[0]:
            # print(f"{get_post_date_or_time()[0]} months ago")
            month_difference = (
                month_dict[current_post_date[0]] - month_dict[compare_date[0]]
            )
            # print(f"{month_difference} months ago")
            return f"{month_difference} months ago"

    elif compare_date[2] != current_post_date[2]:
        # print(f"{get_post_date_or_time()[2]} years ago")
        year_difference = int(current_post_date[2]) - int(compare_date[2])
        # print(f"{year_difference} years ago")
        return f"{year_difference} years ago"


# if the current day differers from the post date in the db then this will change using data from the get_time_ago function
def change_dates(table_name, date_lst):
    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute(f"SELECT * from {table_name}")
    for i in mycursor:
        # print(i)
        author = i[0]
        date = i[1]
        post_time = i[2]
        post = i[3]
        post_file = i[4]
        placeholder_date = i[5]
        id = i[6]
        date_lst.append(date)
        # print(date,post_time)

    for date in date_lst:
        mycursor.execute(
            f"UPDATE {table_name} SET placeholder_date = %s WHERE post_date = %s",
            (get_time_ago(date), date),
        )
        conn.commit()
    mycursor.close()

    date_lst.clear()
    return True


# checks if a file is in the allowed list
def allowed_file(filename):
    # print(filename)
    # return '.' in filename and filename.split('.',)[1].lower() in ALLOWED_EXTENSIONS
    extension = filename.split(".")[1].lower()
    if "." in filename and extension in ALLOWED_EXTENSIONS:
        return True

    else:
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    lst = []  # list that holds all post
    date_lst = []
    like_lst = []  # list that holds all post that the currently signed user has liked
    like_lst_id = (
        []
    )  # list that holds all post id that the currently signed user has liked
    change_dates("Post_Table", date_lst)
    date_lst.clear()  # have to clear the list so it doesnt overwrite the post date
    if request.method == "GET":
        lst.clear()  # have to clear post list so it doesnt display post more than once
        post_date = time.ctime()

        # gets all post from Post_Table db and puts them into a list to send to frontend
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(f"SELECT * FROM Post_Table")
        for post_data in mycursor:
            lst.append(post_data)
        mycursor.close()

        # if signed in this will return all  currently liked post
        if "username" in session:
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                f"SELECT * FROM Likes WHERE name = %s", session["username"]
            )
            for i in mycursor:
                like_lst.append(i)
            mycursor.close()

            for i in like_lst:
                like_lst_id.append(i[1])

        data = {
            "all post": lst[::-1],
            "extensions": ALLOWED_EXTENSIONS,
            "post date": split_compare_date(post_date),
            "like lst": like_lst,
            "like lst id": like_lst_id,
            "time":post_date
        }
        print(post_date)

        return render_template(
            "index.html", data=data
        )  # on GET request loads the home page and sends the data variable that holds all personal data to html frontend

    elif request.method == "POST":
        # print/debug request.form to get all input data from html
        post = request.form.get(
            "post-field"
        )  # assigns the post input field from html using the assigned name 'post-field' to the python variable post
        post = post.capitalize()  # capitalize all post
        post_date = time.ctime()

        if "file" in request.files:
            file = request.files[
                "file"
            ]  # searches the input fields for a uploaded file
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(
                    os.path.join(app.config["UPLOAD_FOLDER"], filename)
                )  # saves the uploaded file to the set path of UPLOAD_FOLDER

                try:
                    im = Image.open(fr"{DIRNAME}\{filename}")
                    newsize = (100, 100)
                    im1 = im.resize(newsize)
                    im1.save(fr"{DIRNAME}\{filename}")

                except:
                    pass

                # inserts new post and file into db
                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(
                    "INSERT INTO Post_Table (author,post_date,post_time,post,post_file) VALUES (%s,%s,%s,%s,%s)",
                    (
                        session["username"],
                        split_compare_date(post_date),
                        calculate_post_time(post_date),
                        post,
                        filename,
                    ),
                )
                conn.commit()
                mycursor.close()
                return redirect("/")

            elif "file" not in request.files:
                return redirect("/")

            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                "INSERT INTO Post_Table (author,post_date,post_time,post) VALUES (%s,%s,%s,%s)",
                (
                    session["username"],
                    split_compare_date(post_date),
                    calculate_post_time(post_date),
                    post,
                ),
            )
            conn.commit()
            mycursor.close()
            return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # resetting the username and password fields to protect previously logged in user
        username = ""
        password = ""

        return render_template("login.html")

    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # queries the db for any users with the requested username
        if username and password != "":
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                f"SELECT * FROM Twitter_Users WHERE username = '{username}'"
            )
            result = mycursor.fetchall()

            # compares all matching usernames and checks the password stored in the db to the requested password entered
            for i in result:
                passwd_check = bcrypt.check_password_hash(i[2], password)

            # if username and password are found in db then sets the session id to the requested username and logins the user in then redirects to home page
            if passwd_check == True:
                session["username"] = username
                mycursor.close()
                return redirect(f"/")

            # if requested password doesnt match and password in db then flashes message and reloads the page
            elif passwd_check == False:
                mycursor.close()
                flash("No password found")
                return redirect("/login")

        # if user attempts to login when fields or empty flashes message and reloads page
        elif username and password == "" or username == "" or password == "":
            print("You must fill in the username and password fields")
            flash("You must fill in the username and password fields")
            return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def create_account():
    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        # print(request.form)
        name = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        compare_password = request.form["compare-password"]
        gender = request.form["gender"]
        age = request.form["age"]
        birthday = request.form["birthday"]
        join_date = time.ctime()

        # using the bcrypt library hashes the password
        hash_passwd = bcrypt.generate_password_hash(password).decode("utf-8")

        # checks if both requested passwords in html form match then checks db if there is already a user with the requested username
        if password == compare_password:
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                f"SELECT * FROM Twitter_Users where username = %s", (username)
            )
            myresult = mycursor.fetchone()

            # if there is no user in the db with the requsted password creates a new entry using all requested data from html form and sets the session id to requested username
            if myresult == None:
                mycursor.close()
                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(
                    "INSERT INTO Twitter_Users (name,username,password, email,privilege,gender,age,birthday,join_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        name,
                        username,
                        hash_passwd,
                        email,
                        "user",
                        gender,
                        age,
                        birthday,
                        join_date,
                    ),
                )
                conn.commit()
                mycursor.close()
                session["username"] = username
                return redirect(f"/profile/{session['username']}/settings")

            # if there already is a user with the requested username then flashes message to user that says "Username Already Exists"
            elif myresult != None:
                # print('username already exists')
                flash("Username Already Exists")
                return redirect("/register")

        # if both passwords in html form dont match then reloads the page
        else:
            flash("Passwords do not match")
            return redirect("/register")


@app.route("/<username>", methods=["GET", "POST"])
def profile(username):
    user_post = []
    profile_stuff = []
    like_lst = []
    like_lst_id = []
    followers = []
    following = []
    post_date = time.ctime()

    if request.method == "GET":
        # queries the db for all post with the username from the route and sends it to the user_post list
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(f"SELECT * FROM Post_Table WHERE author=%s", username)
        for i in mycursor:
            user_post.append(i)
        mycursor.close()

        # queries the db and finds the entry with username from the route
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(f"SELECT * FROM Twitter_Users WHERE username = %s", username)
        for i in mycursor:
            profile_stuff.append(i)
        mycursor.close()

        # user is logged in then returns allpost from requested user that logged user has liked
        if "username" in session:
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                f"SELECT * FROM Likes WHERE name = %s", session["username"]
            )
            for i in mycursor:
                like_lst.append(i)
            mycursor.close()

            for i in like_lst:
                like_lst_id.append(i[1])

        # returns the list of all users the requested user follows
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(f"SELECT * FROM Follow WHERE follower = %s ", username)
        for j in mycursor:
            followers.append(j[0])
        mycursor.close()

        # returns the list of all users that the requested user is following
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(f"SELECT * FROM Follow WHERE name = %s ", username)
        for j in mycursor:
            following.append(j)
        mycursor.close()

        # if user if logged in then creates a variable for the html to display if logged in user is following the requested user
        conn = mysql.connect()
        mycursor = conn.cursor()
        if "username" in session:
            mycursor.execute(
                f"SELECT * FROM Follow WHERE name = %s ", session["username"]
            )
            all_ready_followed = mycursor.fetchone()
            mycursor.close()
        else:
            all_ready_followed = " "

        # checks the db for the requested user if not found flashes message 'This user does not exist'
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(f"SELECT * FROM Twitter_Users where username = %s", (username))
        myresult = mycursor.fetchone()
        mycursor.close()

        if myresult == None:
            flash("This user does not exist")

        # if the requested user has no post then flashes a message saying 'No post yet'
        elif not user_post:
            flash("No post yet")

        data = {
            "username": username,
            "post": user_post[::-1],
            "profile_details": profile_stuff,
            "Allowed Extensions": ALLOWED_EXTENSIONS,
            "post date": split_compare_date(post_date),
            "like lst": like_lst,
            "like id": like_lst_id,
            "Amount of followers": len(followers),
            "Following Amount": len(following),
            "all ready followed": all_ready_followed,
        }

        return render_template(
            "profile.html", data=data, profile_stuff=data["profile_details"]
        )

    elif request.method == "POST":
        # if logged in and user clicks edit account button then sends a post request that redirects to the settings page
        if "Settings" in request.form:
            return redirect(f"/profile/{session['username']}/settings")

        # if logged in user presses the follow button the creates a entry in the db saying logged in user now follows requested user
        if "Follow" in request.form:
            follow = request.form["Follow"]
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                "INSERT INTO Follow (name,follower) VALUES (%s,%s)",
                (session["username"], follow),
            )
            conn.commit()
            mycursor.close()

        # else if loggedin user clicks the unfollow button then queries the db and finds the entry where name is logged in user
        elif "UnFollow" in request.form:
            unfollow = request.form["UnFollow"]
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute("DELETE FROM Follow WHERE name = %s", unfollow)
            conn.commit()
            mycursor.close()

        return redirect(f"/{username}")


@app.route("/<username>/<tab>", methods=["GET", "POST"])
def profile2(username, tab):
    user_post = []
    profile_stuff = []
    like_lst = []
    like_lst_id = []
    comment_lst = []
    comment_lst_id = []
    followers = []
    following = []
    replied_to = []
    date_lst = []
    post_date = time.ctime()
    change_dates("Comments", date_lst)  # updating the dates in the db for all comments

    if request.method == "GET":
        # queries the db and finds the entry with username from the route
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(f"SELECT * FROM Twitter_Users WHERE username = %s", username)
        for i in mycursor:
            profile_stuff.append(i)
        mycursor.close()

        # query the db for all entries with the requested username and puts nameand postID into like lst
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(f"SELECT * FROM Likes WHERE name = %s", username)
        for post in mycursor:
            like_lst.append(post)
        mycursor.close()

        # indexes the items in the like lst for the 2nd element for postID then queries the db for all post with that postID then puts them in another list called 'user_post'
        for id in like_lst:
            post_id = id[1]
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute("SELECT * FROM Post_Table WHERE postID=%s", post_id)
            for j in mycursor:
                user_post.append(j)
            mycursor.close()

        # queries the db for all commets left by the requested user
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM Comments WHERE author = %s", username)
        for j in mycursor:
            comment_lst.append(j)
            # if user has commented on a post more than once this is to stop duplicates and split them up
            if j[6] in comment_lst_id:
                pass
            else:
                comment_lst_id.append(j[6])
        mycursor.close()

        # to display what post the logged in user has replied to first i linked the comment to that post using their 'postID' and put them in a new list
        for id in comment_lst_id:
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute("SELECT * FROM Post_Table WHERE postID = %s", (id))
            for row in mycursor:
                replied_to.append(row)
            mycursor.close()

        # returns the list of all users the requested user follows
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM Follow WHERE follower = %s ", username)
        for j in mycursor:
            followers.append(j)
        mycursor.close()

        # returns the list of all users that the requested user is following
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM Follow WHERE name = %s ", username)
        for j in mycursor:
            following.append(j)
        mycursor.close()

        # if user if logged in then creates a variable for the html to display if logged in user is following the requested user
        if "username" in session:
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                "SELECT * FROM Follow WHERE name = %s ", session["username"]
            )
            all_ready_followed = mycursor.fetchone()
            mycursor.close()
        else:
            all_ready_followed = " "

        # checks the db for the requested user if not found flashes message 'This user does not exist'
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM Twitter_Users where username = %s", (username))
        myresult = mycursor.fetchone()
        mycursor.close()
        if myresult == None:
            flash("This user does not exist")

        # if user tries typing in the search bar the requested user then a tab name that isnt Likes or Replies
        elif tab != "Likes" or tab != "Replies":
            flash(
                f"Hmm... the tab {tab} doesn’t exist. Try searching for something else."
            )

        data = {
            "username": username,
            "post": user_post[::-1],
            "profile_details": profile_stuff,
            "Allowed Extensions": ALLOWED_EXTENSIONS,
            "post date": split_compare_date(post_date),
            "Amount of followers": len(followers),
            "Following Amount": len(following),
            "all ready followed": all_ready_followed,
            "comments": comment_lst[::-1],
            "comment id": comment_lst_id,
            "followers": followers,
            "following": following,
            "tab": tab,
            "replied to": replied_to,
        }

        return render_template(
            "profile_tabs.html",
            data=data,
            username=username,
            profile_stuff=data["profile_details"],
        )

    if request.method == "POST":
        # if logged in user presses the follow button the creates a entry in the db saying logged in user now follows requested user
        if "Follow" in request.form:
            follow = request.form["Follow"]
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                "INSERT INTO Follow (name,follower) VALUES (%s,%s)",
                (session["username"], follow),
            )
            conn.commit()
            mycursor.close()

        # else if loggedin user clicks the unfollow button then queries the db and finds the entry where name is logged in user
        elif "UnFollow" in request.form:
            unfollow = request.form["UnFollow"]
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute("DELETE FROM Follow WHERE name = %s", unfollow)
            conn.commit()
            mycursor.close()

        return redirect(f"/{username}")


# function to call so users can logout
@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username")
        return redirect("/")

    else:
        return redirect("/")


# function to let users or admins delete a post
@app.route("/clear/<int:post_id>")
def clear(post_id):
    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute(f"DELETE FROM Post_Table WHERE postID=%s", (post_id))
    conn.commit()
    mycursor.close()
    return redirect("/")


@app.route("/profile/<username>/settings", methods=["GET", "POST"])
def profile_settings(username):
    profile_stuff = []

    # made a if statement so users cant access other users settings
    if session["username"] == username:
        if request.method == "GET":
            # returns a list of info containing data about the logged in user such as profile image,banner,and description
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                f"SELECT * FROM Twitter_Users WHERE username = %s", username
            )
            for i in mycursor:
                # print(i)
                profile_stuff.append(i)
            mycursor.close()

            return render_template("settings.html", profile_stuff=profile_stuff)

        elif request.method == "POST":
            profile_description = request.form["profile_description"]
            # print(request.form)
            # print(request.files)
            profile_banner = request.files["profile_banner"]
            profile_img = request.files["profile_img"]

            # updates the profile descrition recieved from client side in the db where username is the requested username
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                "UPDATE Twitter_Users SET profile_description = %s WHERE username = %s",
                (profile_description, username),
            )
            mycursor.close()

            # if changing the profile banner this checks if the file is valid then updates it in db
            if profile_banner and allowed_file(profile_banner.filename):
                filename1 = secure_filename(profile_banner.filename)
                profile_banner.save(
                    os.path.join(app.config["UPLOAD_FOLDER"], filename1)
                )

                im = Image.open(fr"{DIRNAME}\{filename1}")
                newsize = (600, 200)
                im1 = im.resize(newsize)
                im1.save(fr"{DIRNAME}\{filename1}")

                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(
                    "UPDATE Twitter_Users SET profile_description = %s,profile_banner = %s WHERE username = %s",
                    (profile_description, filename1, username),
                )
                mycursor.close()

            # if changing the profile image this checks if the file is valid then updates it in db
            if profile_img and allowed_file(profile_img.filename):
                filename2 = secure_filename(profile_img.filename)
                profile_img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename2))

                im = Image.open(fr"{DIRNAME}\{filename2}")
                newsize = (200, 200)
                im1 = im.resize(newsize)
                im1.save(fr"{DIRNAME}\{filename2}")

                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(
                    "UPDATE Twitter_Users SET profile_description = %s,profile_img = %s WHERE username = %s",
                    (profile_description, filename2, username),
                )
            conn.commit()
            mycursor.close()
            return redirect(f"/{session['username']}")
    else:
        flash("Please login using the correct username and password")
        return render_template("setting.html")


@app.route("/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    user_post = []
    comments = []
    date_lst = []
    like_lst = []
    change_dates("Comments", date_lst)  # this will update the date and time on the post
    post_date = time.ctime()
    if request.method == "GET":
        # queries the db for a post with a requested post id
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(f"SELECT * FROM Post_Table WHERE postID=%s", post_id)
        for i in mycursor:
            user_post.append(i)
        mycursor.close()

        # queries the db for all comments with a post id matching the post
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(f"SELECT * FROM Comments WHERE commentID=%s", post_id)
        for i in mycursor:
            comments.append(i)
        mycursor.close()

        # if user is logged in queries the db for a entry containing logged in user and if they have liked the post with requested post id
        if "username" in session:
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute(
                f"SELECT * FROM Likes WHERE id=%s AND name=%s",
                (post_id, session["username"]),
            )
            for i in mycursor:
                like_lst.append(i)
            mycursor.close()
            
        # queries the db checking if logged in user is a admin if True sets a variable allowing admins to delete post
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(
            "SELECT * FROM Twitter_Users WHERE username = %s", session["username"]
        )
        maybe_admin = mycursor.fetchone()
        if maybe_admin[4] == "admin":
            admin_status = True
        else:
            admin_status = False
        mycursor.close()

        # if post has no comments flashes a message 'No comments yet'
        if not comments:
            flash("No comments yet")

        data = {
            "post": user_post,
            "Allowed Extensions": ALLOWED_EXTENSIONS,
            "post date": split_compare_date(post_date),
            "comments": comments[::-1],
            "admin status": admin_status,
        }

        # if logged in user has liked the post this will display the like
        if like_lst:
            # return render_template("post.html",user_post=user_post,ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS,post_date=split_compare_date(post_date),comments=comments[::-1],like_lst=like_lst[0])
            return render_template("post.html", data=data, like_lst=like_lst[0])

        # if there is no logged in user this wont display the like this is needed because if no user is logged in then the like_lst variable is undefined
        elif not like_lst:
            # return render_template("post.html",user_post=user_post,ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS,post_date=split_compare_date(post_date),comments=comments[::-1])
            return render_template("post.html", data=data)
    
    elif request.method=="POST":
        comment=request.form.get("comment-field")
        comment=comment.capitalize()
        print(request.form)
        print(request.files)
        if 'file' in request.files:

            file = request.files['file']
            # print(file)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                try:
                    im = Image.open(fr"{DIRNAME}\{filename}")
                    newsize = (100,100)
                    im1 = im.resize(newsize)
                    im1.save(fr"{DIRNAME}\{filename}")

                except:
                    pass

                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute("INSERT INTO Comments (author,post_date,post_time,comment,post_file,commentID) VALUES (%s,%s,%s,%s,%s,%s)", (session["username"],split_compare_date(post_date),calculate_post_time(post_date),comment,filename,post_id))
                conn.commit()
                mycursor.close()
                return redirect(f"/{post_id}")

            elif "file" not in request.files :
                return redirect(f"/{post_id}")

            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute("INSERT INTO Comments (author,post_date,post_time,comment,commentID) VALUES (%s,%s,%s,%s,%s)", (session["username"],split_compare_date(post_date),calculate_post_time(post_date),comment,post_id))
            conn.commit()
            mycursor.close()
            return redirect(f"/{post_id}")


# quick way for admins to switch users to test bugs/ideas like testing if the 
# like button works corretcly istead of liking the post for all users
@app.route("/switch/<username>")
def switch(username):
    session["username"] = username
    return redirect(f"/{username}")


# on the admin page admins can see all users and post can also promote users to
# admin or demote admins to user,delete users,edit db tables like change names,
# delete,create tables,add columns or rename columns in tables
@app.route("/admin/<username>", methods=["GET", "POST"])
def admin(username):
    if request.method == "GET":
        # checks if the requested username is a admin and if requested username is the logged in user
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM Twitter_Users WHERE username = %s", username)
        maybe_admin = mycursor.fetchone()
        if maybe_admin[4] == "admin" and session["username"] == username:
            users = []
            lst = []
            mycursor.close()

            # queries the db for all users and profile data to display on admin page so admins can moderate
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute("SELECT * FROM Twitter_Users")
            user = mycursor.fetchall()
            for i in user:
                users.append(i)
            mycursor.close()

            conn = mysql.connect()
            mycursor = conn.cursor()
            user_headers = [
                x[0] for x in mycursor.description
            ]  # this will extract row headers
            mycursor.close()

            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute("SELECT * FROM Post_Table")
            post = mycursor.fetchall()
            mycursor.close()

            conn = mysql.connect()
            mycursor = conn.cursor()
            post_headers = [
                x[0] for x in mycursor.description
            ]  # this will extract row headers
            mycursor.close()

            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute("SELECT * FROM Repost_Post")
            reported_post = mycursor.fetchall()
            mycursor.close()

            conn = mysql.connect()
            mycursor = conn.cursor()
            report_headers = [
                x[0] for x in mycursor.description
            ]  # this will extract row headers
            mycursor.close()

            # queries the mysqldb for all tables
            conn = mysql.connect()
            mycursor = conn.cursor()
            mycursor.execute("Show tables;")
            all_tables = mycursor.fetchall()
            mycursor.close()

            data = {
                "user headers": user_headers,
                "users": users,
                "post headers": post_headers,
                "post": post,
                "all tables": all_tables,
                "reported post": reported_post,
                "reported headers": report_headers,
            }
            return render_template("admin.html", data=data)

        # if logged in user is not a admin then flashes a message and redirects user to their page
        else:
            flash("You are not a admin")
            return redirect(f"/{session['username']}")

    elif request.method == "POST":
        selected_table = request.form.get("tables")
        create_table = request.form.get("new-table-name")
        create_table_column = request.form.get("new-table-column")
        create_table_column_type = request.form.get("new-column-types")
        create_table_column_size = request.form.get("new-column-type-size")

        delete_column = request.form.get("delete-column")
        add_column = request.form.get("add-column")
        add_column_types = request.form.get("add-column-types")
        add_column_type_size = request.form.get("add-column-type-size")
        old_column_name = request.form.get("old-column-name")
        new_column_name = request.form.get("new-column-name")
        delete_user = request.form.get("delete-user")
        make_admin = request.form.get("change-user-status-admin")
        make_user = request.form.get("change-user-status-user")

        report = request.form.get("report")

        if selected_table is not None:
            if create_table:
                print(
                    f"({create_table_column} {create_table_column_type}({create_table_column_size})"
                )
                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(
                    f"CREATE TABLE {create_table} ({create_table_column} {create_table_column_type}({create_table_column_size}))"
                )
                conn.commit()
                mycursor.close()
                print(f"{create_table} has been created")

            if delete_column != "":
                print(f"going to delete '{delete_column}' from '{selected_table}'")
                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(f"ALTER TABLE {selected_table} DROP {delete_column}")
                conn.commit()
                mycursor.close()

            if add_column != "":
                print(
                    f"adding column '{add_column}' to '{selected_table}' type '{add_column_types}' with a size of '{add_column_type_size}'"
                )
                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(
                    f"ALTER TABLE {selected_table} ADD {add_column} {add_column_types}({add_column_type_size}) NOT NULL"
                )
                conn.commit()
                mycursor.close()

            if old_column_name != "" and new_column_name != "":
                print(
                    f"changing column '{old_column_name}' to '{new_column_name}' in table '{selected_table}'"
                )
                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(
                    f"ALTER TABLE {selected_table} RENAME COLUMN {old_column_name} TO {new_column_name}"
                )
                conn.commit()
                mycursor.close()

        else:
            if delete_user:
                delete_user = delete_user.split(",")
                table_name = delete_user[0]
                delete_user = delete_user[1]
                delete_user_id = delete_user[2]
                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(
                    f"DELETE FROM {table_name} WHERE personID = %s", delete_user_id
                )
                conn.commit()
                mycursor.close()

            if make_admin:
                make_admin = make_admin.split(",")
                table_name = make_admin[0]
                new_admin_username = make_admin[1]
                new_admin_id = make_admin[2]
                new_user_privilege = make_admin[3]
                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(
                    f"UPDATE {table_name} SET privilege = %s WHERE personID = %s",
                    (new_user_privilege, new_admin_id),
                )
                conn.commit()
                mycursor.close()

            if make_user:
                make_user = make_user.split(",")
                table_name = make_user[0]
                username = make_user[1]
                user_id = make_user[2]
                new_user_privilege = make_user[3]
                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute(
                    f"UPDATE {table_name} SET privilege = %s WHERE personID = %s",
                    (new_user_privilege, user_id),
                )
                conn.commit()
                mycursor.close()
                # print(f"{username} has been demoted to {new_user_privilege}")

            if report:
                conn = mysql.connect()
                mycursor = conn.cursor()
                mycursor.execute("DELETE FROM Repost_Post WHERE postID = %s", report)
                conn.commit()
                mycursor.close()

        return redirect(f"/admin/{session['username']}")


# when the client side sends a signal called 'message' to server side this function is called
@socketio.on("message")
def handle_message(post):
    room = post[
        "type"
    ]  # because i reused js functions i need to seperate them into rooms so it doesnt create entries in more than 1 db table
    post_date = time.ctime()  # returns the current time and date

    # if the js function to create a new post or retweet a post is called then this if statement is ran
    if post["type"] == "newPost" or post["type"] == "retweetPost":
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(
            "INSERT INTO Post_Table (author,post_date,post_time,post) VALUES (%s,%s,%s,%s)",
            (
                session["username"],
                split_compare_date(post_date),
                calculate_post_time(post_date),
                post["message"],
            ),
        )
        conn.commit()
        mycursor.close()

        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM Post_Table WHERE post = %s", (post["message"]))
        current_post = mycursor.fetchall()

        row_headers = [x[0] for x in mycursor.description]  # this will extract row headers
        mycursor.close()
        post = dict(zip(row_headers, current_post[-1]))

        join_room(room)  # joins the room to emit a signal

        # the emit function sends a signal called 'message' to client side that runs the 'message' function
        emit(
            "message", post, broadcast=True, to=room
        )  # setting broadcast to True means if 2 users are currently on the sage page as the socket then both
        # the 'to' attribute says send this data to the specific room this is needed because i reuse js functions


# when the client side sends a signal called 'changeLike' to server side this function is called
@socketio.on("changeLike")
def changeLikes(data):
    if data["status"] == "like":
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(
            "INSERT INTO Likes (name,id) VALUES (%s,%s) ", (data["user"], data["id"])
        )
        conn.commit()
        mycursor.close()

    elif data["status"] == "unlike":
        conn = mysql.connect()
        mycursor = conn.cursor()
        mycursor.execute(
            "DELETE FROM likes WHERE name = %s AND id = %s", (data["user"], data["id"])
        )
        conn.commit()
        mycursor.close()


# when the client side sends a signal called 'makeComment' to server side this function is called
@socketio.on("makeComment")
def comment(data):
    post_date = time.ctime()  # return the current time and date
    room = data[
        "type"
    ]  # because i reused js functions i need to seperate them into rooms so it doesnt create entries in more than 1 db table
    join_room(room)  # joins the room to emit a signal

    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute(
        "INSERT INTO Comments (author,post_date,post_time,comment,commentID) VALUES (%s,%s,%s,%s,%s)",
        (
            session["username"],
            split_compare_date(post_date),
            calculate_post_time(post_date),
            data["comment"],
            data["commentID"],
        ),
    )
    conn.commit()
    mycursor.close()

    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM Comments WHERE comment = %s", (data["comment"]))
    current_post = mycursor.fetchall()

    row_headers = [x[0] for x in mycursor.description]  # this will extract row headers
    mycursor.close()
    data = dict(
        zip(row_headers, current_post[-1])
    )  # after inserting a new entry in the db this will query that entry and the column headers to send to client side

    # the emit function sends a signal called 'message' to client side that runs the 'message' function
    emit(
        "message", data, broadcast=True, to=room
    )  # setting broadcast to True means if 2 users are currently on the sage page as the socket then both
    # the 'to' attribute says send this data to the specific room this is needed because i reuse js functions


# if logged in users report a post this will send a notification to admins by 
# creating a entry in the db displaying who reported the post and what post it is
@socketio.on("reportPost")
def report(data):
    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute(
        "INSERT INTO Repost_Post (reported_by,postID) VALUES (%s,%s)",
        (data["user"], data["id"]),
    )
    conn.commit()
    mycursor.close()


if __name__ == "__main__":
    socketio.run(app,debug=True)
