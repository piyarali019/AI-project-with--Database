from flask_login import LoginManager
from sqlalchemy import create_engine
from flask import Flask
from sqlalchemy.orm import Session
from flask_restful import Resource, Api


engine = create_engine("sqlite:///database.sqlite3")
session=Session(engine)
app = Flask(__name__)
api=Api(app)
app.app_context().push()
login_manager=LoginManager(app)