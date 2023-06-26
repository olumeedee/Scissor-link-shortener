
from . import db
from flask_login import UserMixin

# Creating the database models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.Text(), nullable=False)
    urls = db.relationship('url', backref='user', lazy=True)

    def __repr__(self):
        return f"User <{self.username}>"
    
class url(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    long_url = db.Column(db.String(255), nullable=False, unique=True)
    short_url = db.Column(db.String(255), nullable=False, unique=True)
    custom_url = db.Column(db.String(255), nullable=False, unique=True)
    clicks = db.Column(db.Integer(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Url <{self.long_url}, {self.short_url}>"