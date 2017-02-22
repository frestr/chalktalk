from chalktalk import app
from flask import render_template, request, url_for, redirect, abort
from chalktalk.feedbackforms import Feedbackform
import chalktalk.database

database_url = 'sqlite:///dummy.db'
db = chalktalk.database.DatabaseManager(database_url)

app.secret_key = 'development key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/lecturelist')
def lecturelist():
    return render_template('lecturelist.html')


@app.route('/createlecturelist')
def createlecturelist():
    return render_template('createlecturelist.html')


@app.route('/feedback/<lecture_id>', methods=['POST', 'GET'])
def feedbackform(lecture_id):
    lecture = db.session.query(chalktalk.database.Lecture).filter_by(id=lecture_id).first()
    if lecture is None:
        abort(404)
    subjects = db.session.query(chalktalk.database.Subject).filter_by(lecture_id=lecture.id).all()

    if request.method == 'POST':
        for subject in subjects:
            keys = ['{}_keyword'.format(subject.id),
                    '{}_rating'.format(subject.id),
                    '{}_comment'.format(subject.id)]
            if (keys[0] in request.form and
                    keys[1] in request.form and
                    keys[2] in request.form):
                print(request.form[keys[0]],
                      request.form[keys[1]],
                      request.form[keys[2]])

    return render_template('feedbackform.html',
                           lecture_id=lecture_id,
                           lecture=lecture,
                           subjects=subjects)


@app.route('/lecturefeedback/<lecture_id>')
def lecturefeedback(lecture_id):
    lecture = db.session.query(chalktalk.database.Lecture).filter_by(id=lecture_id).first()
    if lecture is None:
        abort(404)
    subjects = db.get_subject_values(lecture)
    print(subjects)
    return render_template('lecturefeedback.html', subjects=subjects)


@app.route('/lecturertest')
def lecturertest():
    return render_template('lecturertest.html')

