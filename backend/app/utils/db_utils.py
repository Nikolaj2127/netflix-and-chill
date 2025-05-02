from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_users_table():
    class User(db.Model):
        __tablename__ = 'Users'
        
        user_id = db.Column(db.Integer, primary_key=True)
        embedding = db.Column(db.PickleType, nullable=False)

    db.create_all()