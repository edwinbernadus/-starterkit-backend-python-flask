from flask import Flask
from markupsafe import escape
from flask import request, jsonify

from flask import Flask
from flask_sock import Sock
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
import json
from dataclasses import dataclass

db = SQLAlchemy()
app = Flask(__name__)
app.debug = True
DATABASE_URI = 'postgresql://postgres:Testing1@localhost:5432/flask_db'
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
sock = Sock(app)
db.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=False, nullable=False)
    email = db.Column(db.String)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }


with app.app_context():
    db.create_all()


# //web_socket
@sock.route('/ws')
def echo(ws):
    while True:
        data = ws.receive()
        print("data", data)
        output = "reply: " + data.decode()
        ws.send(output)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# //get
@app.route('/hello')
def hello2():
    return 'Hello2, World'


# //routing_id
@app.route("/greet/<name>")
def hello(name):
    return f"Hello3, {escape(name)}!"


# //post
@app.route('/submit_item', methods=['POST'])
def submit():
    # //json_convert
    data = request.get_json()
    data['title'] = data['title'] + ' hello'
    # Do something with the data
    return data


@app.route('/info_header')
def info_header():
    # //get_header
    authorization = request.headers.get('authorization')
    return 'Your authorization is: {}'.format(authorization)

def cleanItems(inputs):
    result_dict = [u.__dict__ for u in inputs]
    for i in result_dict:
        del i['_sa_instance_state']
    return result_dict


@app.route("/users")
def user_list():
    # //sql_select_list
    users = db.session.execute(db.select(User).order_by(User.username)).scalars().all()
    result_dict = cleanItems(users)
    return jsonify(result_dict)

@app.route("/users/create", methods=["GET"])
def user_create():
    user = User(
        username="user1",
        email="email1@email.com",
    )
    # //sql_create
    db.session.add(user)
    db.session.commit()
    print("user", user)
    return jsonify(user.to_dict())

@app.route("/users/<int:id>")
def user_detail(id):
    user = db.get_or_404(User, id)
    print("user", user)
    return jsonify(user.to_dict())

@app.route("/users/<int:id>", methods=['POST'])
def user_update(id):
    data = request.get_json()
    user = db.get_or_404(User, id)
    user.email = data['email']
    # //sql_update
    db.session.commit()
    return jsonify(user.to_dict())

@app.route("/users/delete/<int:id>", methods=["GET"])
def user_delete(id):
    user = db.get_or_404(User, id)
    db.session.delete(user)
    db.session.commit()
    print("user", user)
    return "deleted"

@app.route("/users/total", methods=["GET"])
def user_total():
    # //sql_count
    total = db.session.query(User).count()
    return str(total)

