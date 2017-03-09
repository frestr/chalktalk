#!/usr/bin/env python3
from chalktalk import database
from datetime import datetime
import os

# Start with a clean file
try:
    os.remove('dummy.db')
except FileNotFoundError:
    pass

# Instantiate database
db = database.DatabaseManager('sqlite:///dummy.db')

# Add a course, lecturer and student
course1 = db.add_course('TDT4140', 'Programvareutvikling', 'V2017')
course2 = db.add_course('TDT4145', 'Datamodellering og databaser', 'V2017')
course3 = db.add_course('TMA4100', 'Statistikk', 'H2016')
course4 = db.add_course('LOL1337', 'Leet', 'V9999')

lecturer1 = db.add_lecturer('7b96eab9-b69e-4b8c-9636-1da868207864', 'Ola Nordmann')
lecturer2 = db.add_lecturer('7c9fb9dd-67cc-4976-8c1b-bd14fd71ac75', 'Kari Kari')
student = db.add_student('ec56354e-767b-4dbd-a129-0fda4359f45c', 'Per Hansen')

# Add the student and lecturer to the course
db.add_student_to_course(student, course1)

db.add_lecturer_to_course(lecturer1, course1)
db.add_lecturer_to_course(lecturer1, course2)
db.add_lecturer_to_course(lecturer1, course3)

db.add_lecturer_to_course(lecturer2, course4)

# Add lectures and some subjects
lecture1 = db.add_lecture(course1, datetime.now(), 'MTDT', [lecturer1])
subject1 = db.add_subject(lecture1, 'Programvare')
subject2 = db.add_subject(lecture1, 'Utvikling')

lecture2 = db.add_lecture(course1, datetime.now(), 'MTDT', [lecturer1])
subject3 = db.add_subject(lecture2, 'Java')
subject4 = db.add_subject(lecture2, 'Python')

# Add feedback to the lecture and its subjects
feedback1 = db.add_lecture_feedback(student, lecture1, 'BAD!')
db.add_subject_feedback(feedback1, subject1, 5, 'Easy')
db.add_subject_feedback(feedback1, subject2, 2, 'Hard')
db.add_subject_feedback(feedback1, subject1, 1, 'Easy')
db.add_subject_feedback(feedback1, subject1, 1, 'Easy')
db.add_subject_feedback(feedback1, subject2, 2, 'Hard')
db.add_subject_feedback(feedback1, subject2, 4, 'Hard')

feedback2 = db.add_lecture_feedback(student, lecture2, 'Good!')
db.add_subject_feedback(feedback2, subject3, 3, 'java is hard')
db.add_subject_feedback(feedback2, subject4, 5, 'python is ezpz')

db.save_changes()
