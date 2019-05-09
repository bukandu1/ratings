"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')

@app.route('/users')
def user_list():
    """Show the list of users."""

    #Return list of User objects
    users = User.query.all()
    return render_template('user_list.html', users=users)

@app.route('/register', methods=["GET"])
def reg_page():
    """Send to reg page """

    return render_template('reg-form.html')

@app.route('/register', methods=["POST"])
def reg_process():
    """Process registration and redirect to homepage."""

    # Retrieve variables from form and set to variables
    user_email = request.form.get("email")
    user_pswd = request.form.get("password")

    # Try to get user from db, create user if not in db
    try:
        user_obj = User.query.filter_by(email=user_email, 
                                        password=user_pswd).one()
    except:
        user_obj = User(email=user_email, password=user_pswd)
        db.session.add(user_obj)
        db.session.commit()

    # Redirect to homepage
    return redirect("/")

@app.route("/login")
def login():
    return render_template('login-page.html')

@app.route("/login-process", methods=["POST"])
def login_process():
    #retrieve email and password from login-form
    user_email = request.form.get("email")
    password = request.form.get("password")

    try:
        #check to see if user in db by email 
        #if password matches, query database, retrieve user id and add to session
        user_obj = User.query.filter_by(email=user_email, password=password).one()
        session['user_id'] = user_obj.user_id
        flash("Good job! You're logged in!!!")
        return redirect("/")
        
    except:
        flash("Uh oh! Password/email address is incorrect. It's okay...you can try again")
        return redirect("/login")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
