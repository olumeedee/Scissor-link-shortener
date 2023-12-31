from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_caching import Cache
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os


app = Flask(__name__)

load_dotenv()

base_dir = os.path.dirname(os.path.realpath(__file__))

uri = os.environ.get('DATABASE_URL')

# app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///' + os.path.join(base_dir,'cndsn2.db')
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300


db = SQLAlchemy(app)
migrate = Migrate(app, db)
cache = Cache(app)
limiter = Limiter(get_remote_address)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


from .import routes
from .models import User, Url


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.before_request
def create_tables():
    db.create_all()
