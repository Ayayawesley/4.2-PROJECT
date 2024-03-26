from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)


class Timetable(db.Model):

    __tablename__ = 'timetable'

    id = db.Column(db.Integer, primary_key=True)
    venue = db.Column(db.String(255), nullable=False)
    venue_size = db.Column(db.String(50), nullable=False)
    num_students = db.Column(db.Integer, nullable=False)
    lec_name = db.Column(db.String(255), nullable=False)
    course_name = db.Column(db.String(255), nullable=False)
    unit_name = db.Column(db.String(255), nullable=False)
    year_of_study = db.Column(db.String(50), nullable=False)
    day_of_week = db.Column(db.String(50), nullable=False)
    time_from = db.Column(db.String(10), nullable=False)
    time_to = db.Column(db.String(10), nullable=False)

def serialize_timetable(timetable):
    return {
        'id': timetable.id,
        'venue': timetable.venue,
        'venue_size': timetable.venue_size,
        'num_students': timetable.num_students,
        'course_name': timetable.course_name,
        'lec_name': timetable.lec_name,
        'unit_name': timetable.unit_name,
        'year_of_study': timetable.year_of_study,
        'day_of_week': timetable.day_of_week,
        'time_from': timetable.time_from,
        'time_to': timetable.time_to,
    }

with app.app_context():
    db.create_all()

class TimetableResource(Resource):
    def get(self):
        timetables = Timetable.query.all()
        serialized_timetables = [serialize_timetable(timetable) for timetable in timetables]
        print(serialized_timetables)
        return jsonify(serialized_timetables)

    def post(self):

        try:
            print("here")
            data = request.json

            # Check for collision
            collision_check = Timetable.query.filter_by(
                venue=data['venue'],
                lec_name=data['lec_name'],
                day_of_week=data['day_of_week'],
                time_from=data['time_from'],
                time_to=data['time_to']
            ).first()

            lec_collision = Timetable.query.filter_by(
                lec_name=data['lec_name'],
                day_of_week=data['day_of_week'],
                time_from=data['time_from'],
                time_to=data['time_to']
            ).first()

            if collision_check:
                return {'message': 'Collision detected. Venue already allocated for the specified time.'}, 409
            elif lec_collision:
                return {'message': f"Lecturer, {data['lec_name']} already allocated for the specified time."}, 409

            new_timetable_entry = Timetable(
                venue=data['venue'],
                venue_size=data['venue_size'],
                num_students=data['num_students'],
                course_name=data['course_name'],
                lec_name=data['lec_name'],
                unit_name=data['unit_name'],
                year_of_study=data['year_of_study'],
                day_of_week=data['day_of_week'],
                time_from=data['time_from'],
                time_to=data['time_to']
            )

            db.session.add(new_timetable_entry)
            db.session.commit()

            return {'201': 'success'}
        
        except Exception as e:

            print(e)


api.add_resource(TimetableResource, '/timetable')

if __name__ == '__main__':
    
    app.run(debug=True)
