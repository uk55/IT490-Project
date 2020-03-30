from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
from functools import wraps


import datetime
from flask_cors import CORS, cross_origin



# from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,get_jwt_claims)
# from flask_jwt import JWT
# import sqlite3


app = Flask(__name__, static_url_path='/static')
cors = CORS(app)

db = SQLAlchemy()

app.config['SECRET_KEY'] = 'Th1s1ss3cr3t'
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///library.db'
# local
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/library'
# Prod
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:user@db:3306/library'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.before_first_request
def createTable():
    db.create_all()
    db.session.commit()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(70))
    name = db.Column(db.String(50))
    password = db.Column(db.String(200))
    admin = db.Column(db.Boolean)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    purpose = db.Column(db.String(120))
    status = db.Column(db.String(15))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'purpose': self.purpose,
            'status': self.status,
            'id': self.id,
        }


class Allocate_room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    allocated = db.Column(db.String(50), nullable=False)
    room_no = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50),  nullable=False)
    start_time = db.Column(db.String(50), nullable=False)
    end_time = db.Column(db.String(50), nullable=False)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        print(token)

        if not token:

            return jsonify({'message': 'a valid token is missing'})

        try:
            print("hello checked")
            data = jwt.decode(token, app.config['SECRET_KEY'])
            print("check")
            print(data)
            current_user = Users.query.filter_by(
                public_id=data['public_id']).first()
            print(current_user)
        except Exception as err:
            print(err)

            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator


@app.route('/register', methods=['POST'])
def signup_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(public_id=str(uuid.uuid4()),
                     name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'registered successfully'})


@app.route('/register_librarian', methods=['POST'])
def register_librarian():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(public_id=str(uuid.uuid4()),
                     name=data['name'], password=hashed_password, admin=True)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'registered successfully'})


@app.route('/login', methods=['POST'])
def login_user():

    auth = request.get_json()

    user = Users.query.filter_by(name=auth.get("username")).first()

    if check_password_hash(user.password, auth.get("password")):
        token = jwt.encode({'public_id': user.id, 'admin': user.admin, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})


@app.route('/users', methods=['GET'])
def get_all_users():

    users = Users.query.filter_by(admin="0").all()

    result = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin

        result.append(user_data)

    return jsonify({'users': result})


@app.route('/room', methods=['POST'])
@token_required
def create_room(current_user):

    data = request.get_json()

    new_room = Room(name=data['name'],
                    purpose=data['purpose'], status=data['status'])
    db.session.add(new_room)
    db.session.commit()

    return jsonify({'message': 'new room created'})


@app.route('/room/<name>', methods=['PUT'])
@token_required
def update_room(name):
    room = request.get_json()
    get_room = Room.query.filter_by(name=name).first()

    if room.get('status'):
        get_room.status = room['status']
    if room.get('purpose'):
        get_room.purpose = room['purpose']

    db.session.add(get_room)
    db.session.commit()

    return make_response(jsonify({"room": room}))


@app.route('/rooms/empty', methods=['GET'])
@token_required
def get_rooms(current_user):

    rooms = Room.query.filter_by(status="empty").all()

    output = []
    for room in rooms:

        room_data = {}
        room_data['name'] = room.name
        room_data['purpose'] = room.purpose
        room_data['status'] = room.status
        output.append(room_data)

    return jsonify({'list_of_rooms': output})


@app.route('/rooms/<room_id>', methods=['DELETE'])
@token_required
def delete_room(current_user, room_id):
    room = Room.query.filter_by(id=room_id, user_id=current_user.id).first()
    if not room:
        return jsonify({'message': 'room does not exist'})

    db.session.delete(room)
    db.session.commit()

    return jsonify({'message': 'Room deleted'})


@app.route('/allocate_room', methods=['POST'])
@token_required
def allocate_room(current_user):

    data = request.get_json()

    allocation = Allocate_room(allocated=data['allocated'], room_no=data['room_no'],
                               date=data['date'], start_time=data['start_time'], end_time=data['end_time'])
    db.session.add(allocation)

#    room = Room.query.filter_by(name='room_no').first()
#    room.status = 'Occupied'
    db.session.commit()

    return jsonify({'message': 'allocated'})


@app.route('/allocate_rooms', methods=['GET'])
@token_required
def get_allocated(current_user):

    allocate_room = Allocate_room.query.all()

    list_of_allocations = []
    for room in allocate_room:

        room_data = {}
        room_data['allocated'] = room.allocated
        room_data['room_no'] = room.room_no
        room_data['date'] = room.date
        room_data['start_time'] = room.start_time
        room_data['end_time'] = room.end_time
        list_of_allocations.append(room_data)

    return jsonify({'list_of_allocations': list_of_allocations})


@app.route('/free_rooms/<room_no>', methods=['DELETE'])
@token_required
def allocated_delete_room(current_user, room_no):
    room = Allocate_room.query.filter_by(room_no=room_no).first()
    if not room:
        return jsonify({'message': 'room does not exist'})

    db.session.delete(room)
    db.session.commit()

    return jsonify({'message': 'Room deleted'})

if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=False, host='0.0.0.0')
