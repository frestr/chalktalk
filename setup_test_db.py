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
lecture1 = db.add_lecture(course1,
                          datetime(2017, 3, 10, 14, 15),
                          'MTDT',
                          [lecturer1])
subject1 = db.add_subject(lecture1, 'Programvare')
subject2 = db.add_subject(lecture1, 'Utvikling')

lecture2 = db.add_lecture(course1,
                          datetime(2017, 3, 14, 12, 15),
                          'MTDT',
                          [lecturer1])
subject3 = db.add_subject(lecture2, 'Java')
subject4 = db.add_subject(lecture2, 'Python')

lecture3 = db.add_lecture(course1,
                          datetime(2017, 3, 18, 14, 15),
                          'MTDT',
                          [lecturer1])
subject5 = db.add_subject(lecture3, 'SEMAT')
subject6 = db.add_subject(lecture3, 'Scrum')

lecture4 = db.add_lecture(course1,
                          datetime(2017, 3, 20, 12, 15),
                          'MTDT',
                          [lecturer1])
subject7 = db.add_subject(lecture4, 'Pekka')
subject8 = db.add_subject(lecture4, 'Testing')

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

feedback3 = db.add_lecture_feedback(student, lecture3, 'Good!')
db.add_subject_feedback(feedback3, subject5, 1, 'I had some trouble')
db.add_subject_feedback(feedback3, subject6, 3, 'Nice explanation')

feedback4 = db.add_lecture_feedback(student, lecture4, 'Good!')
db.add_subject_feedback(feedback4, subject7, 5, 'Awesome!')
db.add_subject_feedback(feedback4, subject8, 4, 'Ok i guess')

db.save_changes()
