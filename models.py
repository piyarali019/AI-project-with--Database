from datetime import datetime
from sqlalchemy.sql import func
from flask_login import UserMixin
from main import app, login_manager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Configure application
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'

# Initialize database
db = SQLAlchemy(app)

# Login manager loader
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    password = db.Column(db.String(length=128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer())
    uids = db.relationship('Deck', backref='user', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password_correction(self, attempted_password):
        return check_password_hash(self.password, attempted_password)

    def __repr__(self):
        return f'<User {self.username}>'

# Deck model
class Deck(db.Model):
    __tablename__ = 'deck'
    deck_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    deck_rate = db.Column(db.String(), nullable=False, default="Medium")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<Deck {self.name}>'


class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'{self.name}'


# Card model
class Card(db.Model):
    __tablename__ = 'card'
    card_id = db.Column(db.Integer(), primary_key=True)
    front = db.Column(db.String(), nullable=False, unique=True)
    deck_id = db.Column(db.Integer(), db.ForeignKey("deck.deck_id"))
    card_rate = db.Column(db.String(), nullable=False, default="Medium")
    card_date = db.Column(db.DateTime(), onupdate=func.now(), default=func.now())
    back = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Card {self.front}>'


class Question(db.Model):
    __tablename__ = 'Questions'  # Make sure this matches the name of the table in your database
    question_id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)




