from pip._vendor.requests.packages.urllib3 import request

from chalktalk import app
from flask import render_template, request, url_for, redirect
from .feedbackforms import Feedbackform

app.secret_key = 'development key'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/lecturer')
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