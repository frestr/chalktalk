from chalktalk import app
from flask import render_template, request, url_for, redirect, abort
import chalktalk.database

database_url = 'sqlite:///dummy.db'
db = chalktalk.database.DatabaseManager(database_url)

app.secret_key = 'development key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/courselist/')
def courselist():
    courses = db.session.query(chalktalk.database.Course).all()

    for course in courses:
        print(course.full_name)
    return render_template('courselist.html', courses=courses)


@app.route('/lecturelist/<int:course_id>')
def lecturelist(course_id):
    course = db.session.query(chalktalk.database.Course).get(course_id)
    return render_template('lecturelist.html', course=course)


@app.route('/createlecturelist')
def createlecturelist():
    return render_template('createLecturelist.html')


@app.route('/feedback/<int:lecture_id>', methods=['POST', 'GET'])
def feedbackform(lecture_id):
    lecture = db.session.query(chalktalk.database.Lecture).get(lecture_id)

    ##### NB : This should be the student giving the feedback, not just a 
    ##### random student like now (just for testing)
    student = db.session.query(chalktalk.database.Student).first()
    #####

    if lecture is None:
        abort(404)
    subjects = db.session.query(chalktalk.database.Subject).filter_by(lecture_id=lecture.id).all()

    valid_form = True
    if request.method == 'POST':
        lecture_feedback = db.add_lecture_feedback(student, lecture, '')
        for subject in subjects:
            keys = ['{}_keyword'.format(subject.id),
                    '{}_rating'.format(subject.id),
                    '{}_comment'.format(subject.id)]
            if (keys[0] in request.form and
                    keys[1] in request.form and
                    keys[2] in request.form):
                db.add_subject_feedback(lecture_feedback,
                                        subject,
                                        request.form[keys[1]],
                                        request.form[keys[2]])
            else:
                valid_form = False
                break

        if valid_form:
            db.save_changes()
            return redirect('/lecturelist/{}'.format(lecture.course_id))

    return render_template('feedbackform.html',
                           lecture_id=lecture_id,
                           lecture=lecture,
                           subjects=subjects)


@app.route('/lecturefeedback/<int:lecture_id>')
def lecturefeedback(lecture_id):
    lecture = db.session.query(chalktalk.database.Lecture).filter_by(id=lecture_id).first()
    if lecture is None:
        abort(404)
    subjects = db.get_subject_values(lecture)
    return render_template('lecturefeedback.html', subjects=subjects)


@app.route('/lecturertest')
def lecturertest():
    return render_template('lecturertest.html')

@app.route('/addcourse')
def addcourse():
    return render_template('addCourse.html')

