from flask import Flask, request, render_template, redirect, url_for, request, session, flash
from functools import wraps

app = Flask(__name__)

app.secret_key="my precious"

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
@login_required
def home():
        # return 'Welcome To IT490-Group 7'
        return render_template('index.html')

@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials!!!'
        else:
            session['logged_in']=True
            flash("You were just Logged in!")
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash("You have been successfully Logged Out!")
    return redirect(url_for('welcome'))


# Route for handling the Signup page logic
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials!!!'
        else:
            return redirect(url_for('home'))
    return render_template('signup.html', error=error)


if __name__ == '__main__':
    app.run(debug=True)
