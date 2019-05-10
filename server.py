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

@app.route('/users/<user_id>')
def user_info(user_id):
    """Show user info"""

    #Get/query user object with user id
    user = User.query.get(user_id)

    #Send particular attributes to template
    return render_template('user-details.html', user=user)

@app.route('/rating/<movie_id>', methods=['POST'])
def process_rating(movie_id):
    
    #Retrieve the rating from form
    rating = request.form.get("rating")

    #If rating in database, update. Else create a new rating
    if session.get('user_id'):
        user_id = session.get('user_id')
        
        #Query to see if user has rated movie
        user_rating = Rating.query.filter_by(user_id=user_id, 
                                                movie_id=movie_id).first()

        #If not NONE, update
        if user_rating:
            #Does exist. Update.
            user_rating.score = rating
            db.session.add(user_rating)
            db.session.commit()
        else:
            #Doesnt exist. Add. 
            db.session.add(Rating(score=rating, movie_id=movie_id, user_id=user_id))
            db.session.commit()

        return redirect("/movies")

    else:
        flash("You must be logged in to rate a movie.")
        return redirect("/login")

@app.route('/movies')
def movie_list():
    """Show the list of movies."""

    #Return list of Movie objects
    movies = Movie.query.all()
    return render_template('movie_list.html', movies=movies)

@app.route('/movies/<movie_id>')
def movie_info(movie_id):
    """Show movie info"""

    #Get/query movie object with user id
    movie = Movie.query.get(movie_id)

    #Send particular attributes to template
    return render_template('movie-details.html', movie=movie)

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
        url = "/users/" + str(session['user_id'])
        return redirect(url)
        
    except:
        flash("Uh oh! Password/email address is incorrect. It's okay...you can try again")
        return redirect("/login")

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user_id', None)
   flash("You're logged out. Cool.")
   return redirect("/")

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
