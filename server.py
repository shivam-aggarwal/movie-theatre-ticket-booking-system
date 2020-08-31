from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import json, os, uuid

#init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
#database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#init db
db = SQLAlchemy(app)
#init marshmallow
ma = Marshmallow(app)

#Product clas
class Ticket(db.Model):
    id = db.Column(db.String(36), primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    phoneNumber = db.Column(db.String(10), nullable=False)
    timing = db.Column(db.DateTime, nullable=False)
    date_time_lastModified = db.Column(db.DateTime, default = datetime.now)
    def __init__(self, name, phoneNumber, timing, date_time_lastModified = None):
        self.id = str(uuid.uuid1())
        self.name = name
        self.phoneNumber = phoneNumber
        self.timing = timing
        if date_time_lastModified is not None:
            self.date_time_lastModified = date_time_lastModified
#ticket schema
class TicketSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'phoneNumber', 'timing')
#Init schema
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many = True)
def validName(name:str):
    return len(name) > 0 and name.isalpha()
def validPhoneNumber(phoneNumber:str):
    return len(phoneNumber) == 10 and phoneNumber.isnumeric()
def validtiming(timing :datetime):
    now = datetime.now()
    return (timing > now)

#create a ticket
@app.route('/book', methods=['POST'])
def book_ticket():
    try:
        name = str(request.json['name'])
        if not validName(name):
            return json.dumps({"Error Message" : "Name not valid"})
        phoneNumber = str(request.json['phoneNumber'])
        if not validPhoneNumber(phoneNumber):
            return json.dumps({"Error Message" : "phoneNumber not valid"})
        timing = datetime.strptime(request.json['timing'], '%d-%m-%Y %H:%M')
        if not validtiming(timing):
            return json.dumps({"Error Message" : "Timing not valid"})
        new_ticket = Ticket(name, phoneNumber, timing)
        count = Ticket.query.filter_by(timing=timing).count()
        if count < 20:
            try:
                db.session.add(new_ticket)
                db.session.commit()
            except Exception as e:
                print(e)
                return json.dumps({"Error Message" : "couldn't add element"})
        else:
            return json.dumps({"Error Message" : "Can't book more than 20 tickets for this timing"})
    except Exception as e:
        return json.dumps({"Error Message": "Invalid fields provided"})
    return ticket_schema.jsonify(new_ticket)

#update a ticket
@app.route('/book/<_id>', methods=['PUT'])
def upadate_ticket(_id):
    try:
        _id = str(_id)
        print(_id)
        timing = datetime.strptime(request.json['timing'], '%d-%m-%Y %H:%M')
        if not validtiming(timing):
            return json.dumps({"Error Message" : "Timing not valid"})
        count = Ticket.query.filter_by(id=_id).count()
        if count == 1:
            try:
                Ticket.query.filter_by(id=_id).update({'timing':timing})
                db.session.commit()
                new_ticket = Ticket.query.filter_by(id=_id).first()
            except Exception as e:
                return json.dumps({"Error Message" : "couldn't update element"})
        else:
            return json.dumps({"Error Message" : "Ticket id doesnot exist"})
    except Exception as e:
        return json.dumps({"Error Message": "Invalid fields provided"})
    return ticket_schema.jsonify(new_ticket)

# view all the tickets for a particular time
@app.route('/tickets/<timing>', methods=['GET'])
def gets_tickets(timing):
    try:
        timing = datetime.strptime(timing, '%d-%m-%Y %H:%M')
        if not validtiming(timing):
            return json.dumps({"Error Message" : "Timing not valid"})
        all_tickets = Ticket.query.filter_by(timing = timing).all()
        return tickets_schema.jsonify(all_tickets)
    except Exception as e:
        return json.dumps({"Error Message": "Invalid fields provided"})
    
#view the user’s details based on the ticket id.
@app.route('/user/<_id>', methods=['GET'])
def gets_user(_id):
    try:
        _id = str(_id)
        try:
            new_ticket = Ticket.query.filter_by(id=_id).first()
        except Exception as e:
            return json.dumps({"Error Message" : "couldn't find element"})
    except Exception as e:
        return json.dumps({"Error Message": "Invalid fields provided"})
    return ticket_schema.jsonify(new_ticket)

# delete ticket.
@app.route('/book/<_id>', methods=['DELETE'])
def delete_product(_id):
    try:
        _id = str(_id)
        new_ticket = Ticket.query.get(_id)
        db.session.delete(new_ticket)
        db.session.commit()
        return ticket_schema.jsonify(new_ticket)
    except:
        return json.dumps({"Error Message" : "couldn't delete ticket by this id"})

@app.route('/', methods=['GET'])
def index():
    return jsonify({'msg' : 'Hello World'})

#run server
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)    