from http.client import HTTPResponse
from tabnanny import check
from urllib import response
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, marshal_with, fields
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash



# create the object of Flask
app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

app.config['SECRET_KEY'] = 'hardsecretkey'



# SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:nabeel123@localhost/notes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)




# DB models schema
class User(db.Model):

    __tablename__ = 'user_table'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(125), nullable=False)
    password_hash = db.Column(db.String(125), nullable=False)
    notes = db.relationship('Note', back_populates='user')


class Catagory(db.Model):

    __tablename__ = 'catagory_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(125), nullable=False)
    notes = db.relationship('Note', back_populates='catagory')


class Note(db.Model):

    __tablename__ = 'note_table'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_table.id'))
    Catagory_id = db.Column(db.Integer, db.ForeignKey('catagory_table.id'))
    user = db.relationship('User', back_populates='notes')
    catagory = db.relationship('Catagory', back_populates='notes')


    def __repr__(self):
        return None


notesField = {
    'id': fields.Integer,
    'content': fields.String
}


@auth.verify_password
def authentication(username, password):

    if username and password:
        
        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password_hash, password):
            return True

    return False


# class based views
class Register(Resource):

    @marshal_with(notesField)
    def post(self):
        data = request.json
        print(data)

        user = User.query.filter_by(username=data['username']).first()
        
        # if user:
        #     return 'username already Exist'

        try:
            user = User(username=data['username'], password_hash=generate_password_hash(data['password']))

            db.session.add(user)
            db.session.commit()
            return 'SUCCESS: HERE TODO'
        except Exception as e:
            return e


# todo not completed yet have to change logic because of update in 
# db schema
class Notes(Resource):

    @auth.login_required
    # marshal is basically serializer
    @marshal_with(notesField)
    def get(self):
        notes = Note.query.all()
        return notes

    @auth.login_required
    @marshal_with(notesField)
    def post(self):
        # taking json data from request and add it into db
        data = request.json
        note = Note(content=data['content'])
        db.session.add(note)
        db.session.commit()

        notes = Note.query.all()
        return notes


# todo not completed yet have to change logic because of update in 
# db schema
class SpecificNote(Resource):

    @auth.login_required
    @marshal_with(notesField)
    def get(self, pk):

        note = Note.query.filter_by(id=pk).first()
        return note

    @auth.login_required
    @marshal_with(notesField)
    def put(self, pk):

        data = request.json
        note = Note.query.filter_by(id=pk).first()
        note.content = data['content']
        db.session.commit()

        # return response only
        notes = Note.query.all()
        return notes

    @auth.login_required
    @marshal_with(notesField)
    def delete(self, pk):
        note = Note.query.filter_by(id=pk).first()
        db.session.delete(note)
        db.session.commit()

        notes = Note.query.all()
        return notes




# adding resoures and creating an endpoints
api.add_resource(Register, '/v1/register')
api.add_resource(Notes, '/v1/note')
api.add_resource(SpecificNote, '/v1/note/<int:pk>')


if __name__ == '__main__':
    app.run(debug=True)
