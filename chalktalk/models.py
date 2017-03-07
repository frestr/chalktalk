from sqlalchemy import Column, Integer, String, DateTime, Table
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from chalktalk.database import Base
from flask_login import UserMixin


# This is used for many-to-many relations
relation_tables = {
        'student_course':
            Table('student_course_relation', Base.metadata,
                Column('student_id', Integer, ForeignKey('student.id')),
                Column('course_id', Integer, ForeignKey('course.id'))
            ),
        'lecturer_course':
            Table('lecturer_course_relation', Base.metadata,
                Column('lecturer_id', Integer, ForeignKey('lecturer.id')),
                Column('course_id', Integer, ForeignKey('course.id'))
            ),
        'lecturer_lecture':
            Table('lecturer_lecture_relation', Base.metadata,
                Column('lecturer_id', Integer, ForeignKey('lecturer.id')),
                Column('lecture_id', Integer, ForeignKey('lecture.id'))
            )
}


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    uuid = Column(String(512))
    name = Column(String(256))
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }


class Student(User):
    __tablename__ = 'student'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    courses = relationship(
            'Course',
            secondary=relation_tables['student_course'],
            back_populates='students')

    lecture_feedbacks = relationship('Lecture_feedback', back_populates='student')

    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }


class Lecturer(User):
    __tablename__ = 'lecturer'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    courses = relationship(
            'Course',
            secondary=relation_tables['lecturer_course'],
            back_populates='lecturers')

    lectures = relationship(
            'Lecture',
            secondary=relation_tables['lecturer_lecture'],
            back_populates='lecturers')

    __mapper_args__ = {
        'polymorphic_identity': 'lecturer'
    }


class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    code_name = Column(String(12))
    full_name = Column(String(256))
    semester = Column(String(5))

    students = relationship(
            'Student',
            secondary=relation_tables['student_course'],
            back_populates='courses')

    lecturers = relationship(
            'Lecturer',
            secondary=relation_tables['lecturer_course'],
            back_populates='courses')

    lectures = relationship('Lecture', back_populates='course')


class Lecture(Base):
    __tablename__ = 'lecture'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    parallel = Column(String(32))

    course_id = Column(Integer, ForeignKey('course.id'))
    course = relationship('Course', back_populates='lectures')

    lecturers = relationship(
            'Lecturer',
            secondary=relation_tables['lecturer_lecture'],
            back_populates='lectures')

    feedbacks = relationship('Lecture_feedback', back_populates='lecture')

    subjects = relationship('Subject', back_populates='lecture')


class Subject(Base):
    __tablename__ = 'subject'
    id = Column(Integer, primary_key=True)
    keyword = Column(String(128))

    lecture_id = Column(Integer, ForeignKey('lecture.id'))
    lecture = relationship('Lecture', back_populates='subjects')

    feedbacks = relationship('Subject_feedback', back_populates='subject')


class Lecture_feedback(Base):
    __tablename__ = 'lecture_feedback'
    id = Column(Integer, primary_key=True)
    overall_comment = Column(String(1024))

    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship('Student', back_populates='lecture_feedbacks')

    lecture_id = Column(Integer, ForeignKey('lecture.id'))
    lecture = relationship('Lecture', back_populates='feedbacks')

    subject_feedbacks = relationship('Subject_feedback', back_populates='lecture_feedback')


class Subject_feedback(Base):
    __tablename__ = 'subject_feedback'
    id = Column(Integer, primary_key=True)
    comprehension_rating = Column(Integer)
    comment = Column(String(512))

    lecture_feedback_id = Column(Integer, ForeignKey('lecture_feedback.id'))
    lecture_feedback = relationship('Lecture_feedback', back_populates='subject_feedbacks')

    subject_id = Column(Integer, ForeignKey('subject.id'))
    subject = relationship('Subject', back_populates='feedbacks')
