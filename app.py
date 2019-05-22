from flask import jsonify, request, Response
import json
from settings import app, JWT_Config
from dbModels import Book, User
from functools import wraps

import jwt
import sys


# books validator
def validBookObject(bookObject):
	if 'name' in bookObject and 'price' in bookObject and 'isbn' in bookObject:
		return True
	else:
		return False


# credentials validator
def validCredentials(data):
	if len(data) == 2 and 'username' in data and 'password' in data:
		if isinstance(data['username'], str) and isinstance(data['password'], str):
			return True
	return False


def token_required(f):

	@wraps(f)
	def wrapper(*args, **kwargs):
		token = request.args.get('token')
		try:
			jwt.decode(token, JWT_Config['key'])
		except Exception as e:
			print("JWT Exception:{}".format(str(e)), file=sys.stderr)
			return "You are not authorised"
		return f(*args, **kwargs)
	return wrapper


@app.route('/login', methods=['POST'])
def get_token():
	request_data = request.get_json()
	if not validCredentials(request_data):
		return "Wrong input"
	username = request_data['username']
	password = request_data['password']
	print(username, password)
	print(type(username), type(password))
	if User.username_password_match(username, password):
		token = jwt.encode(JWT_Config['payload'], JWT_Config['key'], JWT_Config['algorithm'])
		return token
	else:
		return "Wrong credentials"


# GET
# Get all the books if token passed is correct:
# /books?token=4646hi3234iam4535valid9090
@app.route('/books')
@token_required
def get_books():
	obj = Book.get_all_books()
	return jsonify(books=[i.serialize for i in obj])


# GET
# Get the book by isbn
@app.route('/books/<int:isbn>')
@token_required
def get_book(isbn):
	obj = Book.get_book_isbn(isbn)
	if obj:
		return jsonify(obj.serialize)
	else:
		return Response("The book with such ISBN wasn't found", status=404)


# POST
# Add a new book
@app.route('/books', methods=['POST'])
@token_required
def add_book():
	received = request.get_json()
	if validBookObject(received):
		new_book = {
			"name": received['name'],
			"price": received['price'],
			"isbn": received['isbn']
		}
		if Book.add_book(**received):
			response = Response("The book is added", 201, mimetype='application/json')
			response.headers["Location"] = "books/" + str(new_book["isbn"])
		else:
			response = Response("Something went wrong! Check the logs!", status=400)
	else:
		invalidBookObjectErrorMsg = {
			"error": "Invalid book object passed in request",
			"helpstring": "Data passed in similar to this {'name': 'bookname', 'price': 7.89, 'isbn': 23424}"
		}
		response = Response(json.dumps(invalidBookObjectErrorMsg), status=400, mimetype='application/json')
	return response


# PUT
# replace the existing book or add one if it doesn't exist
# The request should consist all the keys needed to create a book
# 'isbn' will go in the url
# others will be like { 'name' = ..., 'price' = .... }
@app.route('/books/<int:isbn>', methods=['PUT'])
@token_required
def replace_book(isbn):
	received = request.get_json()
	# Validate the requested data

	received['isbn'] = isbn
	result = Book.replace_book(**received)
	if result == 1:
		response = Response("The book has been replaced", status=201)
	elif result == -1:
		response = Response("Added new book to the end of the list", status=201)
	else:
		response = Response("Something went wrong! Check the logs!", status=400)
	return response


# PATCH
# update only the piece of information
# { 'name': 'Harry Potter' }
@app.route('/books/<int:isbn>', methods=['PATCH'])
@token_required
def update_book(isbn):
	received = request.get_json()
	# Validate the requested data

	received['isbn'] = isbn
	if Book.edit_book(**received):
		response = Response("The book has been updated", status=201)
	else:
		response = Response("Something went wrong! Check the logs!", status=400)
	return response


# DELETE
@app.route('/books/<int:isbn>', methods=['DELETE'])
@token_required
def delete_book(isbn):
	result = Book.delete_book(isbn)
	if result > 0:
		response = Response('%s books have been deleted' % result, status=201)
	else:
		response = Response("The book with such ISBN wasn't found", status=404)
	return response


if __name__ == "__main__":
	app.run()
