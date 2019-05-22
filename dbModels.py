from flask import Flask
from flask_alchemydumps import AlchemyDumps, AlchemyDumpsCommand
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Command
from sqlalchemy.exc import IntegrityError
import json
import sys
from settings import app

db = SQLAlchemy(app)


class Book(db.Model):

    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    isbn = db.Column(db.Integer, nullable=False, unique=True)

    @staticmethod
    def add_book(**kwargs):
        try:
            new_book = Book(**kwargs)
            db.session.add(new_book)
            db.session.commit()
            return 1
        except IntegrityError as e:
            print("SQL Query error: {}".format(str(e)), file=sys.stderr)
            return 0

    @staticmethod
    def get_all_books():
        return Book.query.all()

    @staticmethod
    def get_book_isbn(_isbn):
        book = Book.query.filter_by(isbn=_isbn).first()
        return book

    @staticmethod
    def edit_book(**kwargs):
        book = Book.get_book_isbn(kwargs['isbn'])
        if book is not None:
            try:
                for key, value in kwargs.items():
                    setattr(book, key, value)
                db.session.commit()
            except Exception as e:
                print("Error: {}".format(str(e)), file=sys.stderr)
                return -1
            return 1
        else:
            print("Couldn't find the book with such ISBN", file=sys.stderr)
            return 0

    @staticmethod
    def replace_book(**kwargs):
        found = Book.edit_book(**kwargs)
        if found == 1:
            return 1
        elif found == 0:
            if Book.add_book(**kwargs):
                return -1
        return 0

    @staticmethod
    def delete_book(_isbn):
        result = Book.query.filter_by(isbn=_isbn).delete()
        db.session.commit()
        return result

    @property
    def serialize(self):
        json_object = {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'isbn': self.isbn
        }
        return json_object

    def __repr__(self):
        book_object = {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'isbn': self.isbn
        }
        return json.dumps(book_object)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return str({
            'username': self.username,
            'password': self.password
        })

    @staticmethod
    def username_password_match(_username, _password):
        user = User.query.filter_by(username=_username).filter_by(password=_password).first()
        if user:
            return True
        else:
            return False

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def add_user(_username, _password):
        try:
            new_user = User(username=_username, password=_password)
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError as e:
            print("SQL Query error: {}".format(str(e)), file=sys.stderr)
            return 0
        return 1

# init Alchemy Dumps
manager = Manager(app)
alchemydumps = AlchemyDumps(app, db)
manager.add_command("alchemydumps", AlchemyDumpsCommand)

if __name__ == "__main__":
    manager.run()


