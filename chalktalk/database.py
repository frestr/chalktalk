from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# The models module depend on this, so that's why it's global
Base = declarative_base()

# This must be imported AFTER Base has been instantiated!
from chalktalk.models import User, Student, Lecturer, \
    Course, Lecture, Subject, \
    Lecture_feedback, Subject_feedback


class DatabaseManager():
    def __init__(self, database_url):
        '''Set up SQL Alchemy with the database at 'database_path'

        database_url : URL sent to sqlalchemy. Can e.g. be 'sqlite:////home/bob/database.db'
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

    def _add_user(self, uuid, name, role):
        '''Internal method for generically adding users'''
        if self.session.query(User).filter_by(uuid=uuid).count() != 0:
            return None

        if role == 'student':
            user = Student(uuid=uuid, name=name)
        elif role == 'lecturer':
            user = Lecturer(uuid=uuid, name=name)
        else:
            return None

        self.session.add(user)

        return user

    def add_student(self, uuid, name):
        '''Add a new student

        uuid     : dataporten UUID, in format '7b96eab9-b69e-4b8c-9636-1da868207864'
        name     : full name of student
        '''
        return self._add_user(uuid, name, 'student')

    def add_lecturer(self, uuid, name):
        '''Add a new lecturer

        uuid     : dataporten UUID, in format '7b96eab9-b69e-4b8c-9636-1da868207864'
        name     : full name of lecturer
        '''
        return self._add_user(uuid, name, 'lecturer')

    def add_course(self, code_name, full_name, semester, lecturers=[]):
        '''Add a new course

        code_name : string, e.g. 'TDT4140'
        full_name : full course name, e.g. 'Programvareutvikling'
        semester  : string, in format 'SYYYY' where S is V (spring) or H (autumn), and
                    YYYY is the year, e.g. V2017
        lecturers : list of Lecturer objects. optional
        '''
        if self.session.query(Course). \
                filter_by(code_name=code_name, semester=semester).count() != 0:
            return None

        course = Course(code_name=code_name,
                        full_name=full_name,
                        semester=semester,
                        lecturers=lecturers)
        self.session.add(course)

        return course

    def add_student_to_course(self, student, course):
        '''Add a student to a course's student list

        student : Student object
        courtse : Course object
        '''
        if student not in course.students:
            course.students.append(student)

    def add_lecturer_to_course(self, lecturer, course):
        '''Add a lecturer to a course's lecturer list

        lecturer : Lecturer object
        course   : Course object
        '''
        if lecturer not in course.lecturers:
            course.lecturers.append(lecturer)

    def add_lecture(self, course, date, parallel, lecturers):
        '''Add a lecture

        course    : Course object
        date      : datetime object
        parallel  : string signifying the course parallel/group (e.g. 'MTDT')
        lecturers : list of Lecturer objects
        '''
        lecture = Lecture(course=course,
                          date=date,
                          parallel=parallel,
                          lecturers=lecturers)
        self.session.add(lecture)

        return lecture

    def add_subject(self, lecture, subject_keyword):
        '''Add a lecture subject

        lecture         : Lecture object
        subject_keyword : string with a single keyword
        '''
        subject = Subject(lecture=lecture, keyword=subject_keyword)
        self.session.add(subject)

        return subject

    def add_lecture_feedback(self, student, lecture, overall_comment):
        '''Add feedback to a lecture

        student         : Student object that gives the feedback
        lecture         : Lecture object that the feedback is intended for
        overall_comment : string with comment on the whole lecture
                          (not a single subject)
        '''
        feedback = Lecture_feedback(student=student,
                                    lecture=lecture,
                                    overall_comment=overall_comment)
        self.session.add(feedback)

        return feedback

    def add_subject_feedback(self, lecture_feedback, subject, comprehension_rating, comment):
        '''Add feedback to a lecture subject

        lecture_feedback     : Lecture_feedback object
        subject              : Subject object
        comprehension_rating : integer from 1 to 5
        comment              : string, comment on this subject
        '''
        feedback = Subject_feedback(lecture_feedback=lecture_feedback,
                                    subject=subject,
                                    comprehension_rating=comprehension_rating,
                                    comment=comment)
        self.session.add(feedback)

        return feedback

    def save_changes(self):
        '''Save database changes persistently to SQL database'''
        self.session.commit()

    def get_subject_values(self, lecture):
        data = []
        for subject in lecture.subjects:
            name = subject.keyword
            ratings = [feedback.comprehension_rating for feedback in subject.feedbacks]
            rating_counts = [ratings.count(i) for i in range(1, 6)]
            comments = [(feedback.comprehension_rating, feedback.comment, feedback.lecture_feedback.student.id)
                        for feedback in subject.feedbacks]
            data.append({'name': name,
                         'ratings': rating_counts,
                         'comments': comments})
        return data
