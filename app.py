from http.client import HTTPResponse
from tabnanny import check
from urllib import response
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
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
    catagory_id = db.Column(db.Integer, db.ForeignKey('catagory_table.id'))
    user = db.relationship('User', back_populates='notes')
    catagory = db.relationship('Catagory', back_populates='notes')


    def __repr__(self):
        return None





@auth.verify_password
def authentication(username, password):

    if username and password:
        
        user = User.query.filter_by(username=username).first()

        if not user:
            return False
        if check_password_hash(user.password_hash, password):
            return True

    return False


notesField = {
    'id': fields.Integer,
    'name': fields.String,
    'content': fields.String

}

# class based views
class Register(Resource):

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
            return 'SUCCESS', 200
        except Exception as e:
            return e



class Notes(Resource):


    @auth.login_required
    # marshal is basically serializer
    @marshal_with(notesField)
    def get(self):
        user_id = User.query.filter_by(username=auth.current_user()).first().id
        notes = db.session.query(Catagory.name, Note.id, Note.content).join(Note).filter_by(user_id=user_id).all()
        return notes

    @auth.login_required
    def post(self):

        print(auth.current_user())
        # taking json data from request and add it into db
        data = request.json
        user_id = User.query.filter_by(username=auth.current_user()).first().id
        cat = Catagory.query.filter_by(name=data['catagory']).first()
        if cat is None:
            cat = Catagory(name=data['catagory'])
            db.session.add(cat)
            db.session.commit()

        note = Note(content=data['content'], user_id=user_id, catagory_id=cat.id)
        db.session.add(note)
        db.session.commit()

        return 'Success', 200



class SpecificNote(Resource):

    @auth.login_required
    @marshal_with(notesField)
    def get(self, pk):

        user_id = User.query.filter_by(username=auth.current_user()).first().id
        
        note = Note.query.filter_by(id=pk).first()
        if note is None:
            return 'Not found', 400

        if note.user_id != user_id:
            return 'You are not authorized', 400
        
        note = db.session.query(Catagory.name, Note.id, Note.content).join(Note).filter_by(user_id=user_id).first()
        
        return note

    @auth.login_required
    def put(self, pk):

        user_id = User.query.filter_by(username=auth.current_user()).first().id
        
        note = Note.query.filter_by(id=pk).first()
        if note is None:
            return 'Not found', 400

        if note.user_id != user_id:
            return 'You are not authorized', 400

        data = request.json

        cat = Catagory.query.filter_by(name=data['catagory']).first()
        if cat is None:
            cat = Catagory(name=data['catagory'])
            db.session.add(cat)
            db.session.commit()

        note = Note.query.filter_by(id=pk).first()
        note.content = data['content']
        note.catagory_id = cat.id
        db.session.commit()

        return 'Successfully Updated', 201



    @auth.login_required
    def delete(self, pk):

        user_id = User.query.filter_by(username=auth.current_user()).first().id
        
        note = Note.query.filter_by(id=pk).first()
        if note is None:
            return 'Not found', 400

        if note.user_id != user_id:
            return 'You are not authorized', 400

        note = Note.query.filter_by(id=pk).first()
        db.session.delete(note)
        db.session.commit()
        
        return "Successfully Deleted", 200




# adding resoures and creating an endpoints
api.add_resource(Register, '/v1/register')
api.add_resource(Notes, '/v1/note')
api.add_resource(SpecificNote, '/v1/note/<int:pk>')


if __name__ == '__main__':
    app.run(debug=True)
