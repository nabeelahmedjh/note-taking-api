from flask_sqlalchemy import SQLAlchemy
from .app import app
db = SQLAlchemy()

db = SQLAlchemy(app)



# models
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return self.content


