from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from openclass import Config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./../scrapers/data/queens.db'
db = SQLAlchemy(app)
db.init_app(app)

from opencourse.main.routes import main
app.register_blueprint(main)
