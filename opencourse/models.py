from sqlalchemy import Column, Integer, String, ForeignKey, Time, create_engine
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.schema import UniqueConstraint
from opencourse import db


class Course(db.Model):
    __tablename__ = 'Course'
    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    semester = Column(String)
    sections = relationship("Section", backref='course')
    UniqueConstraint('name', 'semester', name='uix_1')

    def asdict(self):
        sections = [section.asdict() for section in self.sections]
        return {
            'code': self.code,
            'name': self.name,
            'semester': self.semester,
            'sections': sections
        }


class Section(db.Model):
    __tablename__ = 'Section'
    id = Column(Integer, primary_key=True)
    code = Column(String)
    kind = Column(String)
    course_id = Column(Integer, ForeignKey('Course.id'))
    timeslots = relationship("Timeslot", backref='section')
    UniqueConstraint('course_id', 'code', 'kind', name='uix_1')

    def asdict(self):
        timeslots = [timeslot.asdict() for timeslot in self.timeslots]
        return {
            'code': self.code,
            'kind': self.kind,
            'timeslots': timeslots
        }


class Timeslot(db.Model):
    __tablename__ = 'Timeslot'
    id = Column(Integer, primary_key=True)
    day = Column(String)
    start_time = Column(Time)
    end_time = Column(Time)
    section_id = Column(Integer, ForeignKey('Section.id'))

    def asdict(self):
        return {
            'day': self.day,
            'start_time': self.start_time.strftime("%H:%M"),
            'end_time': self.end_time.strftime("%H:%M"),
        }


if __name__ == '__main__':
    db_name = input('Enter name of database to be created (eg: queens): ')
    engine = create_engine("sqlite:///data/{}.db".format(db_name))
    db.create_all(bind=engine)
