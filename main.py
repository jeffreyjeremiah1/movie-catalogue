from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
from pprint import pprint

API_KEY = "0db8f0adf6ad76eda433e3a8ec40e5e3"
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top-movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)
db = SQLAlchemy(app)


class RateMovieForm(FlaskForm):
    rating = FloatField(label="Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    Done = SubmitField('Done')


class AddMoviesForm(FlaskForm):
    movie_title = StringField(label="Movie Title", validators=[DataRequired()])
    add_button = SubmitField('Add Movie')


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


def __repr__(self):
    return f'<Book {self.title}>'


db.create_all()


@app.route("/")
def home():
    all_movies = Movies.query.order_by(Movies.ranking).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["get", "POST"])
def edit():
    form = RateMovieForm()
    if request.method == "POST":
        movie_id = request.args.get('id')
        movie_to_update = Movies.query.get(movie_id)
        movie_to_update.rating = request.form['rating']
        movie_to_update.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form)


@app.route('/add', methods=["GET", "POST"])
def add():
    form = AddMoviesForm()
    if request.method == "POST":
        movie = form.movie_title.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": API_KEY, "query": movie})
        data = response.json()['results']
        return render_template("select.html", options=data)
    return render_template("add.html", form=form)


@app.route('/select', methods=["GET", "POST"])
def select():
    movie_id = request.args.get('id')
    if movie_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_id}"
        response = requests.get(movie_api_url, params={"api_key": API_KEY})
        data = response.json()
        pprint(data)
        new_movie = Movies(
            title=data['title'],
            year=data["release_date"].split('-')[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data['overview']
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))


@app.route('/delete', methods=["GET", "POST"])
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movies.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
