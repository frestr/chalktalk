from chalktalk import app
from flask import render_template, request, url_for, redirect, abort
from .feedbackforms import Feedbackform
import chalktalk.database

database_url = 'sqlite:///dummy.db'
db = chalktalk.database.DatabaseManager(database_url)

app.secret_key = 'development key'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/lecturelist')
def lecturer():
    return render_template('lecturer.html')

@app.route('/createlecturelist')
def createlecturelist():
    return render_template('createlecturelist.html')

@app.route('/feedback/', methods=['post', 'get'])
def feedbackform():
    lecture = "TDT4100"
    subjects = ['Pastasaus', 'Pizzabunn', 'Algoritmer']
    form = Feedbackform()

    if request.method == 'POST':
        return 'Form posted.'
    elif request.method == 'GET':
        return render_template('feedbackform.html', form=form, lecture=lecture, subjects=subjects)

@app.route('/lecturertest')
def lecturertest():
    return render_template('lecturertest.html')

@app.route('/statisticsview/<lecture_id>')
def statisticsview(lecture_id):
    lecture = db.session.query(chalktalk.database.Lecture).filter_by(id=lecture_id).first()
    if lecture is None:
        abort(404)
    subjects = db.get_subject_values(lecture)
    print(subjects)
    return render_template('statisticsview.html', subjects=subjects)

@app.route('/lecturefeedback/<lecture_id>')
def feedbackLecturer(lecture_id):
    lecture = db.session.query(chalktalk.database.Lecture).filter_by(id=lecture_id).first()
    if lecture is None:
        abort(404)
    subjects = db.get_subject_values(lecture)
    print(subjects)
    return render_template('feedbackLecturer.html', subjects=subjects)


