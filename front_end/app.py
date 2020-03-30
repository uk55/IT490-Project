from flask import Flask, render_template, redirect,url_for

import datetime



# from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,get_jwt_claims)
# from flask_jwt import JWT
# import sqlite3


app = Flask(__name__ , static_url_path='/static')

app.config['SECRET_KEY']='Th1s1ss3cr3t'




@app.route("/", methods=['GET','POST'])
def index():
    return render_template("login.html")

@app.route("/logout")
def logout():
    return render_template("login.html")


@app.route("/librarian")
def librarian_dash():
    return render_template("librarian_dashboard.html")

@app.route("/student_dash")
def student_dash():
    return render_template("student_dash.html")



@app.route("/signup_librarian")
def signup_librarian():

    return render_template("registration_librarian.html")


@app.route("/signup")
def signup():

    return render_template("registration.html")


@app.route("/gen_room")
def generate_room():
    return render_template("create_room.html")

@app.route("/assign_room")
def assign_room():
    return render_template("Assign_room.html")

@app.route("/availability")
def availability_room():
    return render_template("room_availability.html")

if __name__ == "__main__":

    app.run(debug=True, port=5000, host='0.0.0.0')


