from chalktalk import database,models
from datetime import datetime

# Instantiate database
db = database.DatabaseManager('sqlite:///:memory:')

# Add a course, lecturer and student
course   = db.add_course('TDT4140', 'Programvareutvikling', 'V2017')
lecturer = db.add_lecturer('7b96eab9-b69e-4b8c-9636-1da868207864', 'Ola Nordmann')
student  = db.add_student('ec56354e-767b-4dbd-a129-0fda4359f45c', 'Per Hansen')

# Add the student and lecturer to the course
db.add_student_to_course(student, course)
db.add_lecturer_to_course(lecturer, course)

# Add a lecture and some subjects
lecture  = db.add_lecture(course, datetime.now(), 'MTDT', [lecturer])
subject1 = db.add_subject(lecture, 'Programvare')
subject2 = db.add_subject(lecture, 'Utvikling')

# Add feedback to the lecture and its subjects
feedback = db.add_lecture_feedback(student, lecture, 'BAD!')
db.add_subject_feedback(feedback, subject1, 5, 'Easy')
db.add_subject_feedback(feedback, subject2, 2, 'Hard')
