import unittest
from chalktalk import database
from chalktalk import models
from datetime import datetime


class TestDatabaseUserCourses(unittest.TestCase):

    def setUp(self):
        self.db = database.DatabaseManager('sqlite:///:memory:')

    def tearDown(self):
        self.db.shutdown_session()

    def add_user(self, uuid, name, role):
        before_count = self.db.session.query(models.User).count()

        if role == 'student':
            self.db.add_student(uuid, name)
        elif role == 'lecturer':
            self.db.add_lecturer(uuid, name)
        else:
            self.fail()

        self.db.save_changes()

        self.assertEqual(self.db.session.query(models.User).count(), before_count+1)
        self.assertEqual(
                self.db.session.query(models.User).
                filter_by(uuid=uuid, name=name).
                count(), 1)

    def test_add_student(self):
        # Try to add the user twice. The first time the user should be properly added,
        # and the second the time nothing should change, because duplicate users
        # are not allowed
        uuid = '4fa2fd2b-9143-47c5-8325-cf43bc26271b'
        name = 'bob'
        self.add_user(uuid, name, 'student')
        with self.assertRaises(AssertionError):
            self.add_user(uuid, name, 'student')

    def test_add_lecturer(self):
        uuid = '1daededb-f85c-44fa-a152-dd7915d30a62'
        name = 'arne'
        self.add_user(uuid, name, 'lecturer')
        with self.assertRaises(AssertionError):
            self.add_user(uuid, name, 'lecturer')

    def add_course(self, code_name, full_name, semester):
        before_count = self.db.session.query(models.Course).count()

        self.db.add_course(code_name, full_name, semester)
        self.db.save_changes()

        self.assertEqual(self.db.session.query(models.Course).count(), before_count+1)
        self.assertEqual(
                self.db.session.query(models.Course).
                filter_by(code_name=code_name, semester=semester).
                count(), 1)

    def test_add_course(self):
        code_name = 'TDT4140'
        full_name = 'Programvareutvikling'
        semester = 'V2017'
        self.add_course(code_name, full_name, semester)
        with self.assertRaises(AssertionError):
            self.add_course(code_name, full_name, semester)


class TestDatabaseAdding(unittest.TestCase):

    def setUp(self):
        self.db = database.DatabaseManager('sqlite:///:memory:')

        self.course = self.db.add_course('TDT4140', 'Programvareutvikling', 'V2017')
        self.lecturer = self.db.add_lecturer('4fa2fd2b-9143-47c5-8325-cf43bc26271b', 'bob')
        self.lecture = self.db.add_lecture(self.course, datetime.now(), 'X', [self.lecturer])
        self.student = self.db.add_student('9fa2fd2b-9143-47c5-8325-cf43bc26271b', 'bob')
        self.subject = self.db.add_subject(self.lecture, 'Python')
        self.lecture_feedback = self.db.add_lecture_feedback(self.student, self.lecture, 'Good')
        self.subject_feedback = self.db.add_subject_feedback(self.lecture_feedback, self.subject, 5, 'Good')

        self.db.save_changes()

    def tearDown(self):
        self.db.shutdown_session()

    def test_add_lecture(self):
        self.assertIn(self.lecture, self.course.lectures)
        self.assertIn(self.lecturer, self.lecture.lecturers)

    def test_add_subject(self):
        self.assertIn(self.subject, self.lecture.subjects)

    def test_add_lecture_feedback(self):
        self.assertIn(self.lecture_feedback, self.lecture.feedbacks)

    def test_add_subject_feedback(self):
        self.assertIn(self.subject_feedback, self.subject.feedbacks)

    def test_add_student_to_course(self):
        self.db.add_student_to_course(self.student, self.course)
        self.assertIn(self.student, self.course.students)

    def test_add_lecturer_to_course(self):
        self.db.add_lecturer_to_course(self.lecturer, self.course)
        self.assertIn(self.lecturer, self.course.lecturers)

    def test_get_subject_values(self):
        self.subject_feedback = self.db.add_subject_feedback(self.lecture_feedback, self.subject, 1, 'Hard')

        values = [{'name': 'Python', 'ratings': [1, 0, 0, 0, 1], 'comments': [(5, 'Good', self.student.id), (1, 'Hard', self.student.id)]}]

        self.assertEqual(self.db.get_subject_values(self.lecture), values)
