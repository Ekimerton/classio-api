from opencourse import app
from flask import json, jsonify, Blueprint, request
from opencourse.models import Course, Section, Timeslot

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify({'message': 'welcome to opencourse'})

@main.route('/semesters')
def all_semesters():
    query = Course.query.with_entities(Course.semester).distinct()
    semesters = [row.semester for row in query]
    return jsonify({'semesters': semesters})

@main.route('/course')
def all_courses():
    semester = request.args.get("semester", default="2021 Fall", type=str)
    courses = Course.query.filter_by(semester=semester).all()
    codes = [course.code for course in courses]
    return jsonify({'course_codes':codes})


@main.route('/course/<string:code>')
def get_course(code):
    semester = request.args.get("semester", default="2021 Fall", type=str)
    course = Course.query.filter_by(code=code, semester=semester).first()

    if not course:
        return jsonify({'error': 'class not found'}), 404

    course = course.asdict()
    return jsonify({'course_info': course})
