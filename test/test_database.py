import unittest
from chalktalk import database
from chalktalk import models

class TestDatabaseManager(unittest.TestCase):

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
        uuid = '123'
        name = 'bob'
        self.add_user(uuid, name, 'student')
        with self.assertRaises(AssertionError):
            self.add_user(uuid, name, 'student')

    def test_add_lecturer(self):
        uuid = '222'
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
