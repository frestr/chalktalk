from pip._vendor.requests.packages.urllib3 import request

from chalktalk import app
from flask import render_template, request, url_for, redirect


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/lecturer')
def lecturer():
    return render_template('lecturer.html')