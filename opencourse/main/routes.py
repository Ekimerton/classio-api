from opencourse import app
from flask import jsonify, Blueprint
from opencourse.models import Course, Section, Timeslot

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify({'message': 'welcome to opencourse'})


@main.route('/<string:year>/<string:term>/course')
def all_courses(year, term):
    semester = "{} {}".format(year, term)
    courses = Course.query.filter_by(semester=semester).all()
    codes = [course.code for course in courses]
    return jsonify({'class_codes':codes})


@main.route('/<string:year>/<string:term>/course/<string:code>')
def get_course(year, term, code):
    semester = "{} {}".format(year, term)
    courses = Course.query.filter_by(code=code, semester=semester).first()
    courses = courses.asdict()
    print(courses)
    return jsonify(courses)
