from opencourse import app
from flask import json, jsonify, Blueprint, request
from flask_cors import cross_origin
from opencourse.models import Course, Section, Timeslot

main = Blueprint('main', __name__)


@main.route('/')
@cross_origin()
def home():
    return jsonify({'routes': [
        {'/semesters': {'url args': 'None',
                        'description': 'get all semesters provided by classio api'}},
        {'/course': {'url args': 'semester code',
                     'description': 'return all courses for a given semester'}},
        {'/course/<COURSE_CODE>': {'url args': 'semester code',
                                   'description': 'return information about given course code'}},
    ]})


@main.route('/semesters')
@cross_origin()
def all_semesters():
    query = Course.query.with_entities(Course.semester).distinct()
    semesters = [row.semester for row in query]
    return jsonify({'semesters': semesters})


@main.route('/course')
@cross_origin()
def all_courses():
    semester = request.args.get("semester", default="2021 Fall", type=str)
    courses = Course.query.filter_by(
        semester=semester).with_entities(Course.code).distinct()
    codes = [course.code for course in courses]
    return jsonify({'course_codes': codes})


@main.route('/course/<string:code>')
@cross_origin()
def get_course(code):
    semester = request.args.get("semester", default="2021 Fall", type=str)
    course = Course.query.filter_by(code=code, semester=semester).first()

    if not course:
        return jsonify({'error': 'class not found'}), 404

    course = course.asdict()
    return jsonify({'course_info': course})
