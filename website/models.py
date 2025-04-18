from datetime import datetime
from flask_login import UserMixin
from . import db
import pytz


class Diary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Bangkok')))
    level = db.Column(db.String(50), nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)  
    image_caption = db.Column(db.Text, nullable=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "level": self.level,
            "image_filename": self.image_filename,
            "image_caption": self.image_caption
        }


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    diaries = db.relationship('Diary', backref='author', lazy=True)  


class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)   
    timestamp = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Bangkok'))) 
