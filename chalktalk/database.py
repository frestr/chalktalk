from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# The models module depend on this, so that's why it's global
Base = declarative_base()

# This must be imported AFTER Base has been instantiated!
from chalktalk.models import User, Student, Lecturer, \
                             Course, Lecture, Lecture_subject, \
                             Lecture_feedback, Subject_understanding


class DatabaseManager():
    def __init__(self, database_url):
        '''Set up SQL Alchemy with the database at 'database_path'

        database_url can be e.g. 'sqlite:////home/bob/database.db'
        '''
        self.engine = create_engine(database_url, convert_unicode=True)
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=False,
                                                   bind=self.engine))

        global Base
        Base.query = self.session.query_property()

        Base.metadata.create_all(self.engine)

    def shutdown_session(self):
        '''Close the database'''
        self.session.remove()

    def _add_user(self, oauth_id, name, role):
        '''Internal method for generically adding users'''
        if self.session.query(User).filter_by(oauth_id=oauth_id).count() != 0:
            return False

        if role == 'student':
            user = Student(oauth_id=oauth_id, name=name)
        elif role == 'lecturer':
            user = Lecturer(oauth_id=oauth_id, name=name)
        else:
            return False

        self.session.add(user)
        self.save_changes()

        return True

    def add_student(self, oauth_id, name):
        '''Add a new student to the database'''
        return self._add_user(oauth_id, name, 'student')

    def add_lecturer(self, oauth_id, name):
        '''Add a new lecturer to the database'''
        return self._add_user(oauth_id, name, 'lecturer')

    def add_course(self, code_name, full_name, semester, lecturers=[]):
        if self.session.query(Course).filter_by(code_name=code_name, semester=semester).count() != 0:
            return False

        course = Course(code_name=code_name, full_name=full_name, semester=semester, lecturers=lecturers)
        self.session.add(course)
        self.save_changes()

        return True

    def add_student_to_course(self, student, course):
        pass

    def add_lecture(self, course, date, parallel, lecturers):
        lecture = Lecture(course=course, date=date, parallel=parallel, lecturers=lecturers)
        self.session.add(lecture)
        self.save_changes()

    def add_lecture_subject(self, lecture, subject_keyword):
        subject = Lecture_subject(lecture=lecture, keyword=subject_keyword)
        self.session.add(subject)
        self.save_changes()

    def add_feedback(self, student, overall_comment):
        pass

    def add_subject_understanding(self, lecture_feedback, lecture_subject, comprehension_rating, comment):
        pass

    def save_changes(self):
        '''Save database changes persistently to SQL database'''
        self.session.commit()
