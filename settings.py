from flask import Flask
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\albert\\source\\PyRestApi\\database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kuku'

delta = 100

JWT_Config = {
    'payload': {
        'exp': datetime.utcnow() + timedelta(seconds=delta)
    },
    'algorithm': 'HS256',
    'key': app.config['SECRET_KEY']
}

