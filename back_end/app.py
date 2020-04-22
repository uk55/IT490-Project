from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
from functools import wraps
from flask import session
import datetime
from flask_cors import CORS, cross_origin
import pika


now = datetime.datetime.utcnow()
todays_date = now.strftime('%Y-%m-%d %H:%M:%S')
print(todays_date)

# from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,get_jwt_claims)
# from flask_jwt import JWT
# import sqlite3


app = Flask(__name__, static_url_path='/static')
cors = CORS(app)

db = SQLAlchemy()

app.config['SECRET_KEY'] = 'Th1s1ss3cr3t'
## local #
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:sdp150516@localhost:3306/library'
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
    allocated = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    room_no = db.Column(db.Integer, db.ForeignKey('room.id'),nullable=False)
    date = db.Column(db.String(50),  nullable=False)
    start_time = db.Column(db.String(50), nullable=False)
    end_time = db.Column(db.String(50), nullable=False)
    allocated_by = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)


class Contact_us(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    send_to = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    message = db.Column(db.String(10050), nullable=False)
    sended_by = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)



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
            current_user = Users.query.filter_by(id=data['public_id']).first()

            abc = current_user.name

            print("+++++++++++")
            print(abc)
            print("+++++++++++")
            # a = session(abc)

        except Exception as err:
            print("+++===========")
            print(err)
            print("+++===========")

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
    print(user)
    if check_password_hash(user.password, auth.get("password")):
        token = jwt.encode({'public_id': user.id, 'admin': user.admin, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})




@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):
   users = Users.query.filter_by(admin="0").all()
   result = []


   for user in users:
       user_data = {}
       user_data['public_id'] = user.id
       user_data['name'] = user.name
       user_data['password'] = user.password
       user_data['admin'] = user.admin

       result.append(user_data)

   return jsonify({'users': result})

@app.route('/users_admin', methods=['GET'])
@token_required
def get_all_users_admin(current_user):

    print("***************")
    print(current_user.name)
    print("***************")
    users = Users.query.filter_by(admin="1").all()
    result = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.id
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
        room_data['id'] = room.id
        room_data['name'] = room.name
        room_data['purpose'] = room.purpose
        room_data['status'] = room.status
        output.append(room_data)

    return jsonify({'list_of_rooms' : output})




@app.route('/rooms/<room_id>', methods=['DELETE'])
@token_required
def delete_room(room_id):
    room = Room.query.filter_by(id=room_id).first()
    if not room:
        return jsonify({'message': 'room does not exist'})

    db.session.delete(room)
    db.session.commit()

    return jsonify({'message': 'Room deleted'})


@app.route('/allocate_room', methods=['POST'])
@token_required
def allocate_room(current_user):
    a= current_user.id
    print(a)
    data = request.get_json()

    allocation = Allocate_room(allocated=data['allocated'], room_no=data['room_no'],
                               date=data['date'], start_time=data['start_time'], end_time=data['end_time'],allocated_by=a)
    db.session.add(allocation)

    # room = Room.query.filter_by(name='room_no').first()
    # room.status = 'Occupied'
    db.session.commit()

    return jsonify({'message': 'allocated'})


@app.route('/allocate_rooms', methods=['GET'])
@token_required
def get_allocated(current_user):
    a= current_user.id
    # allocate_room = Allocate_room.query.filter_by(allocated_by=a).all()
    allocate_room = Allocate_room.query.join(Users,Allocate_room.allocated==Users.id).add_columns(Users.name,Allocate_room.allocated,Allocate_room.room_no,Allocate_room.date,Allocate_room.start_time,Allocate_room.end_time).filter(Allocate_room.allocated_by==a).all()

    list_of_allocations = []
    for room in allocate_room:

        room_data = {}
        room_data['allocated'] = room.allocated
        room_data['room_no'] = room.room_no
        room_data['date'] = room.date
        room_data['start_time'] = room.start_time
        room_data['end_time'] = room.end_time
        room_data['name'] = room.name

        list_of_allocations.append(room_data)

    return jsonify({'list_of_allocations': list_of_allocations})


@app.route('/allocate_rooms_user', methods=['GET'])
@token_required
def get_allocated_user(current_user):
    a= current_user.id
    # allocate_room = Allocate_room.query.filter_by(allocated_by=a).all()
    allocate_room = Allocate_room.query.join(Users,Allocate_room.allocated==Users.id).add_columns(Users.name,Allocate_room.allocated,Allocate_room.room_no,Allocate_room.date,Allocate_room.start_time,Allocate_room.end_time).all()

    list_of_allocations = []
    for room in allocate_room:

        room_data = {}
        room_data['allocated'] = room.allocated
        room_data['room_no'] = room.room_no
        room_data['date'] = room.date
        room_data['start_time'] = room.start_time
        room_data['end_time'] = room.end_time
        room_data['name'] = room.name

        list_of_allocations.append(room_data)

    return jsonify({'list_of_allocations': list_of_allocations})


@app.route('/free_rooms/<room_no>', methods=['DELETE'])
@token_required
def allocated_delete_room(current_user,room_no):

    room = Allocate_room.query.filter_by(room_no=room_no).first()
    if not room:
        return jsonify({'message': 'room does not exist'})

    db.session.delete(room)
    db.session.commit()

    return jsonify({'message': 'Room deleted'})


@app.route('/contact', methods=['POST'])
@token_required
def create_contact(current_user):
    data = request.get_json()
    message = data['message']
    new_message = Contact_us(send_to=data['send_to'],message=data['message'],sended_by=current_user.id)

    connection = pika.BlockingConnection(pika.ConnectionParameters(
                    'localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='queuename')

    channel.basic_publish(exchange='',
                            routing_key='queuename',
                            body=str(message))
    print(" [x] Sent 'Rabbit Message'")

    connection.close()

    db.session.add(new_message)
    db.session.commit()

    return jsonify({'message': 'new Message sended'})


@app.route('/inbox', methods=['GET'])
@token_required
def get_inbox(current_user):
    a = current_user.id
    print(a)
    contacts = Contact_us.query.join(Users,Contact_us.sended_by==Users.id).add_columns(Users.name,Contact_us.send_to,Contact_us.message,Contact_us.sended_by).filter(Contact_us.send_to==a).all()

    # contacts = Contact_us.query.join(Contact_us).filter_by(Contact_us.send_to==Users.id).all()

    result = []

    for contact_msg in contacts:
        contact_msg_data = {}
        contact_msg_data['send_to'] = contact_msg.send_to
        contact_msg_data['message'] = contact_msg.message
        contact_msg_data['sended_by'] = contact_msg.sended_by
        contact_msg_data['name']= contact_msg.name

        result.append(contact_msg_data)
        print("all messages")
        print(result)

    return jsonify({'result': result})


@app.route('/outbox', methods=['GET'])
@token_required
def get_outbox(current_user):
    a = current_user.id
    contacts = Contact_us.query.join(Users,Contact_us.send_to==Users.id).add_columns(Users.name,Contact_us.send_to,Contact_us.message,Contact_us.sended_by).filter(Contact_us.sended_by==a).all()

    result = []

    for contact_msg in contacts:
        contact_msg_data = {}
        contact_msg_data['send_to'] = contact_msg.send_to
        contact_msg_data['message'] = contact_msg.message
        contact_msg_data['sended_by'] = contact_msg.sended_by
        contact_msg_data['name']= contact_msg.name


        result.append(contact_msg_data)
        print("all messages")
        print(result)

    return jsonify({'result': result})


# @app.route('/contacts/<contact_id>', methods=['DELETE'])
# @token_required
# def delete_contact(current_user, contact_id):
#     contact = Contact_us.query.filter_by(id=contact_id).first()
#     if not contact:
#         return jsonify({'message': 'Message not exist'})

#     db.session.delete(contact)
#     db.session.commit()

#     return jsonify({'message': 'Message deleted'})





if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=False, host='0.0.0.0')