"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, Movie, Rating
# from model import Rating
# from model import Movie

from model import connect_to_db, db
from server import app
from datetime import datetime


def load_users():
    """Load users from u.user into database."""

    print("Users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    print("Movies")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate movies
    Movie.query.delete()

    # Read u.item file and insert data
    for row in open("seed_data/u.item"):
        row = row.rstrip()
        (movie_id, title, release_dt, video_released_dt, imdb_url, gn_unknown, 
         gn_action, gn_adventure, gn_animation, gn_childrens, gn_comedy, 
         gn_crime, gn_documentary, gn_drama, gn_fantasy, gn_film_noir, 
         gn_horror, gn_musical, gn_mystery, gn_romance, gn_scifi, gn_thriller,
         gn_war, gn_western) = row.split('|')

        # Strip trailing date from movie title
        title = title[:-6]

        # Reformat release date as datetime object
        released_at = datetime.strptime(release_dt, "%d-%b-%Y")

        # Create movie object
        movie = Movie(movie_id=movie_id,
                      title=title,
                      released_at=released_at,
                      imdb_url=imdb_url)

        # Add each movie to session to be stored
        db.session.add(movie)

    # Commit added movies to session
    db.session.commit()

def load_ratings():
    """Load ratings from u.data into database."""
    print("Ratings")

    Rating.query.delete()

    #Read u.data file and insert data
    for row in open("seed_data/u.data"):
        row = row.rstrip()
        user_id, movie_id, score, timestamp = row.split('\t')
        #print(row)

        #Create Rating object
        rating = Rating(user_id=user_id, 
                        movie_id=movie_id, 
                        score=score)

        #Add each rating to the session to be stored
        db.session.add(rating)

    #Commit out changes!!!
    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
