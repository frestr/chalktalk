from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# The models module depend on this, so that's why it's global
Base = declarative_base()

# This must be imported AFTER Base has been instantiated!
from probe_website.models import *


class DatabaseManager():
    def __init__(self, database_url):
        """Set up SQL Alchemy with the database at 'database_path'

        database_url can be e.g. 'sqlite:////home/bob/database.db'
        """
        self.engine = create_engine(database_url, convert_unicode=True)
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=False,
                                                   bind=self.engine))

        global Base
        Base.query = self.session.query_property()

        self.setup_relationships()

        Base.metadata.create_all(self.engine)

    def shutdown_session(self):
        """Close the database"""
        self.session.remove()

    def add_student(self, oauth_id):
        pass

    def add_lecturer(self, oauth_id):
        pass

    def add_course(self, codename, full_name, semester, lecturers):
        pass

    def add_student_to_course(self, student, course):
        pass

    def add_lecture(self, course, date, parallel, lecturers):
        pass

    def add_lecture_subject(self, lecture, subject_keyword):
        pass

    def add_feedback(self, student, overall_comment):
        pass

    def add_subject_understanding(self, lecture_feedback, lecture_subject, comprehension_rating, comment):
        pass
