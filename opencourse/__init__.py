from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# from openclass import Config


app = Flask(__name__)
cors = CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./../scrapers/data/queens.db'
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)
db.init_app(app)

from opencourse.main.routes import main
app.register_blueprint(main)
