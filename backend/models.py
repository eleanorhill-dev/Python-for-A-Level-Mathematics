from extensions import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    sname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    uname = db.Column(db.String(100), unique=True, nullable=False)
    pword = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"User with first name {self.fname} and email {self.email}"
    
class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Topic: {self.name}"
    
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False, default='multiple-choice')
    option_a = db.Column(db.String(200), nullable=True)
    option_b = db.Column(db.String(200), nullable=True)
    option_c = db.Column(db.String(200), nullable=True)
    option_d = db.Column(db.String(200), nullable=True)
    correct_answer = db.Column(db.String(200), nullable=True)
    
    topic = db.relationship('Topic', backref=db.backref('questions', lazy=True))

    def __repr__(self):
        return f"Question: {self.question_text} (Type: {self.question_type})"
    
class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    attempts = db.Column(db.Integer, default=1)
    highest_score = db.Column(db.Integer, nullable=False)
    lowest_score = db.Column(db.Integer, nullable=False)
    last_score = db.Column(db.Integer, nullable=False)
    last_attempt_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Score(user_id={self.user_id}, topic_id={self.topic_id}, highest_score={self.highest_score}, attempts={self.attempts})"
