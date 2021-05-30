from sqlalchemy import Column, Integer, String, ForeignKey, Time, create_engine
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import UniqueConstraint

Base = declarative_base()


class Course(Base):
    __tablename__ = 'Course'
    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    semester = Column(String)
    sections = relationship("Section", backref='course')
    UniqueConstraint('name', 'semester', name='uix_1')


class Section(Base):
    __tablename__ = 'Section'
    id = Column(Integer, primary_key=True)
    code = Column(String)
    kind = Column(String)
    course_id = Column(Integer, ForeignKey('Course.id'))
    timeslots = relationship("Timeslot", backref='section')
    UniqueConstraint('course_id', 'code', 'kind', name='uix_1')


class Timeslot(Base):
    __tablename__ = 'Timeslot'
    id = Column(Integer, primary_key=True)
    day = Column(String)
    start_time = Column(Time)
    end_time = Column(Time)
    section_id = Column(Integer, ForeignKey('Section.id'))


if __name__ == '__main__':
    db_name = input('Enter name of database to be created (eg: queens): ')
    engine = create_engine("sqlite:///data/{}.db".format(db_name))
    Base.metadata.create_all(bind=engine)
