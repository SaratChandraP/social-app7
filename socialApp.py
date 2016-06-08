from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from config import SQLALCHEMY_DATABASE_URI
import datetime
# from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)


# Application users
class AppUsers(db.Model):
    user_id = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(50))

    def __init__(self, user_id, email_id):
        self.user_id = user_id
        self.email = email_id


# Relationship between users
class UserRelationship(db.Model):
    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id_1 = db.Column(db.String(20))
    user_id_2 = db.Column(db.String(20))
    status = db.Column(db.String(20))
    action_user_id = db.Column(db.String(20))

    def __init__(self, user_id_one, user_id_two, status, action_id):
        self.user_id_1 = user_id_one
        self.user_id_2 = user_id_two
        self.status = status
        self.action_user_id = action_id


# Messages exchanged between users
class Messages(db.Model):
    msg_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(20))
    receiver_id = db.Column(db.String(20))
    message = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)

    def __init__(self, sender, receiver, message, time):
        self.sender_id = sender
        self.receiver_id = receiver
        self.message = message
        self.timestamp = time


@app.route('/')
def hello():
    return 'Welcome to the App !'


@app.route('/addUser', methods=['POST'])
def add_user():
    user_id = request.json.get('user_id')
    email = request.json.get('email')
    user = AppUsers(user_id, email)
    db.session.add(user)
    try:
        db.session.commit()
        return jsonify({'user': 'added'}), 201
    except:
        return jsonify({"error": "New user not added to DB"}), 500


@app.route('/relation/<action>', methods=['POST'])
def relation(action):
    # Mapping the action to status
    status_dict = {'add': 'Pending', 'accept': 'Friends', 'block': 'Blocked', 'unfriend': 'Unfriended'}
    # Checking for valid actions
    if action not in status_dict.keys():
        return Response(status=404)
    # Parsing POST data
    user_1 = request.form['user_id_1']
    user_2 = request.form['user_id_2']
    action_user = request.form['action_user_id']
    # Determine action and performing the corresponding one
    if action == 'add':
        new_relation = UserRelationship(user_1, user_2, status_dict[action], action_user)
        db.session.add(new_relation)
    else:
        UserRelationship.query.filter_by(user_id_1=user_1, user_id_2=user_2)\
            .update(dict(status=status_dict[action], action_user_id=action_user))
    try:
        db.session.commit()
        return "success"
    except:
        return "error"


@app.route('/getUsers')
def get_users():
    if AppUsers.query.count() == 0:
        return Response(status=204)
    result = []
    for u in AppUsers.query.all():
        tmpdict = {
            'user_id': u.user_id,
            'email': u.email
        }
        result.append(tmpdict)
    return jsonify({'users':result}), 200


@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        user = request.args.get('user_id')
        data = Messages.query.filter((Messages.sender_id==user)|(Messages.receiver_id==user))
        if data.count() == 0:
            return "No messages found"
        msgs = data.all()
        message_array = []
        for msg in msgs:
            tmpdict = {
                'sender': msg.sender_id,
                'receiver': msg.receiver_id,
                'message': msg.message,
                'time': msg.timestamp
            }
            message_array.append(tmpdict)
        return jsonify({'messages': message_array}), 200

    elif request.method == 'POST':
        sender = request.form['sender_id']
        receiver = request.form['receiver_id']
        message = request.form['message']
        time = datetime.datetime.now()
        if Messages.query.filter_by(sender_id=sender, receiver_id=receiver).count() == 0:
            new_message = Messages(sender, receiver, message, time)
            db.session.add(new_message)
        else:
            Messages.query.filter_by(sender_id=sender, receiver_id=receiver)\
                .update(dict(message=message, timestamp=time))
        try:
            db.session.commit()
            return "Message added"
        except:
            return "error"


@app.route('/getFriends')
def get_friends():
    user_id = request.args.get('user_id')
    data = UserRelationship.query.filter((UserRelationship.user_id_1==user_id)|(UserRelationship.user_id_2==user_id)).all()
    friends = []
    for rel in data:
        if rel.user_id_1 != user_id:
            friends.append(rel.user_id_1)
        elif rel.user_id_2 != user_id:
            friends.append(rel.user_id_2)
    return jsonify({'friends': friends}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port='8000')
