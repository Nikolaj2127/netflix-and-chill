from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, nullable=False)
    embedding = db.Column(db.PickleType, nullable=False)

class UserGroups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(80), unique=True, nullable=False)
    user_ids = db.Column(db.PickleType, nullable=False)  # Store user IDs as a list of strings

class Film(db.Model):
    film_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.Text)
    genre = db.Column(db.String(100))
    poster_url = db.Column(db.String(200))

def create_tables():
    db.create_all()