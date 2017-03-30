import unittest
import chalktalk
from chalktalk import views
from chalktalk import database
from datetime import datetime
from chalktalk import settings
from chalktalk import models


class TestViews(unittest.TestCase):

    def setUp(self):
        chalktalk.app.testing = True
        self.app = chalktalk.app.test_client()
        views.db = database.DatabaseManager('sqlite:///:memory:')
        self.db = views.db

        self.student = self.db.add_student('ec56354e-767b-4dbd-a129-0fda4359f45c', 'Per Hansen')
        self.lecturer = self.db.add_lecturer('7b96eab9-b69e-4b8c-9636-1da868207864', 'Ola Nordmann')
        self.db.save_changes()

    def tearDown(self):
        self.db.shutdown_session()

    def test_index_nologin(self):
        rv = self.app.get('/')
        assert b'Log in with Feide' in rv.data

    def login(self, role):
        return self.app.get('/login?role={}'.format(role),
                            follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('student')
        assert b'Course List' in rv.data
        assert b'Log out' in rv.data
        rv = self.logout()
        assert b'Log in with Feide' in rv.data

        rv = self.login('lecturer')
        assert b'Course List' in rv.data
        assert b'Log out' in rv.data
        assert b'Add course' in rv.data
        rv = self.logout()
        assert b'Log in with Feide' in rv.data

        rv = self.login('blah')
        assert b'Log in with Feide' in rv.data

    def test_courselist(self):
        rv = self.login('student')
        rv = self.app.get('/courselist', follow_redirects=True)
        assert b'TDT4140' not in rv.data
        assert b'Programvareutvikling' not in rv.data

        course = self.db.add_course('TDT4140', 'Programvareutvikling', 'V2017')
        self.db.add_student_to_course(self.student, course)
        self.db.save_changes()

        # Still no lectures added, so should not be shown
        rv = self.app.get('/courselist', follow_redirects=True)
        assert b'TDT4140' not in rv.data
        assert b'Programvareutvikling' not in rv.data

        self.db.add_lecture(course, datetime(2017, 3, 10, 14, 15), 'MTDT', [])
        self.db.save_changes()

        rv = self.app.get('/courselist', follow_redirects=True)
        assert b'TDT4140' in rv.data
        assert b'Programvareutvikling' in rv.data

        self.logout()

    def test_lecturelist(self):
        rv = self.login('student')
        rv = self.app.get('/lecturelist/1', follow_redirects=True)
        # Should be redirected when invalid id is specified
        assert b'Course List' in rv.data

        course = self.db.add_course('TDT4140', 'Programvareutvikling', 'V2017')
        self.db.add_student_to_course(self.student, course)
        self.db.save_changes()

        rv = self.app.get('/lecturelist/{}'.format(course.id))
        assert b'Lecture List' in rv.data

        lecture = self.db.add_lecture(course, datetime(2017, 3, 10, 14, 15), 'MTDT', [])
        self.db.add_subject(lecture, 'SUPER FUN')
        self.db.save_changes()

        rv = self.app.get('/lecturelist/{}'.format(course.id))
        assert b'SUPER FUN' in rv.data

        self.logout()

    def test_createlecturelist(self):
        rv = self.login('student')
        course = self.db.add_course('TDT4140', 'Programvareutvikling', 'V2017')
        # self.db.add_student_to_course(self.student, course)
        self.db.save_changes()

        rv = self.app.post('/createlecturelist/{}'.format(course.id))
        assert '403' in rv.status

        self.logout()

        rv = self.login('lecturer')

        # Create mock data here and test

        self.logout()

    def test_feedback(self):
        pass

    def test_lecturefeedback(self):
        pass

    def test_semesteroverview(self):
        pass

    def test_add_course(self):
        pass

    def test_editlecturetags(self):
        pass
