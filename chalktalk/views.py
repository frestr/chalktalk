from chalktalk import app, util
from flask import render_template, request, redirect, abort, url_for, flash
import chalktalk.database
import flask_login
from chalktalk.oauth import DataportenSignin
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
import re
from chalktalk.models import User, Course

database_url = 'sqlite:///dummy.db'
db = chalktalk.database.DatabaseManager(database_url)

app.secret_key = 'development key'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

Breadcrumbs(app=app)


@login_manager.user_loader
def user_loader(user_id):
    # get will return None if not found (this is what flask_login expects)
    user = db.session.query(User).get(user_id)
    return user


@app.teardown_appcontext
def shutdown_database_session(exception=None):
    """Close the database on application shutdown."""
    db.shutdown_session()


@app.route('/')
def index():
    """Render home page if the user is authenticated.
    Otherwise redirect to login page."""
    if flask_login.current_user.is_authenticated:
        # return redirect(url_for('courselist'))
        # @@@ Temporary for testing
        return redirect(url_for('courselist'))
    else:
        return render_template('index.html')


# For testing
@app.route('/login')
def login():
    role = request.args.get('role', '')
    user = None
    if role == 'student':
        user = db.session.query(User).\
                filter_by(uuid='ec56354e-767b-4dbd-a129-0fda4359f45c').first()
    elif role == 'lecturer':
        user = db.session.query(User).\
                filter_by(uuid='7b96eab9-b69e-4b8c-9636-1da868207864').first()

    if user:
        flask_login.login_user(user)
    return redirect(url_for('index'))


@app.route('/__oauth/authorize')
def oauth_authorize():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('index'))
    oauth = DataportenSignin()
    return oauth.authorize()


@app.route('/__oauth/callback')
def oauth_callback():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('index'))
    oauth = DataportenSignin()
    userinfo, groups = oauth.callback()

    if userinfo is None:
        flash('Authentication failed', 'error')
        return redirect(url_for('index'))

    if groups is None:
        flash('Could not fetch groups from feide', 'error')
        return redirect(url_for('index'))

    user = db.session.query(User).filter_by(uuid=userinfo['userid']).first()

    # Add a new user if not already registered
    if user is None:
        role = ''
        for group in groups:
            # All NTNU students/employees are in this group
            if group['id'] == 'fc:org:ntnu.no':
                role = group['membership']['primaryAffiliation']
                break
        if role == 'student':
            user = db.add_student(userinfo['userid'], userinfo['name'])
        elif role == 'employee':
            user = db.add_lecturer(userinfo['userid'], userinfo['name'])
        else:
            flash('You are registered as neither student nor employee in feide')
            return redirect(url_for('index'))

    for group in groups:
        course_pattern = 'fc:fs:fs:emne:ntnu\.no:([A-Z]{3}[0-9]{4}):1'
        match = re.fullmatch(course_pattern, group['id'])
        if match:
            role = group['membership']['fsroles']
            code_name = match.group(1)
            course = db.session.query(Course).filter_by(code_name=code_name).first()
            # If the course exists in the db already, add
            # the user to courses he either takes or lectures
            if course:
                if role == 'STUDENT':
                    db.add_student_to_course(user, course)
                elif role == 'EMPLOYEE':
                    db.add_lecturer_to_course(user, course)
            # If it doesn't exists, add it if the user is a lecturer
            else:
                full_name = group['displayName']
                semester = util.get_semester(group)
                # notAfter in group means that the course is old
                if (role == 'EMPLOYEE' and
                        'notAfter' not in group['membership']):
                    db.add_course(code_name, full_name, semester, [user])

    db.save_changes()
    flask_login.login_user(user)

    # Prevent open redirects
    next = request.args.get('next')
    if not util.is_safe_url(next):
        return abort(400)

    return redirect(next or url_for('index'))


@app.route('/logout')
@flask_login.login_required
def logout():
    """Log current user out and redirect to login page."""
    flask_login.logout_user()
    return redirect(url_for('index'))


@app.route('/courselist/')
@register_breadcrumb(app, '.', 'Course list', 0)
def courselist():
    courses = flask_login.current_user.courses
    return render_template('courselist.html', courses=courses)


def course_list_id(*args, **kwargs):
    """Helper method for breadcrumbs. Gets the course id"""
    course_id = request.view_args['course_id']
    course = db.session.query(chalktalk.database.Course).get(course_id)
    return {'course_id': course.id}


def lecture_list_id(*args, **kwargs):
    """Helper method for breadcrumbs. Gets the lecture id"""
    lecture_id = request.view_args['lecture_id']
    lecture = db.session.query(chalktalk.database.Lecture).filter_by(id=lecture_id).first()
    return {'lecture_id': lecture.id}


@app.route('/lecturelist/<int:course_id>')
@register_breadcrumb(app, '.lecture', 'Lecture List', 1, endpoint_arguments_constructor=course_list_id)
@flask_login.login_required
def lecturelist(course_id):
    course = db.session.query(chalktalk.database.Course).get(course_id)
    return render_template('lecturelist.html', course=course)


@app.route('/createlecturelist/<int:course_id>', methods=['POST', 'GET'])
@register_breadcrumb(app, '.createcourse', 'Create Lecture List', 1, endpoint_arguments_constructor=course_list_id)
def createlecturelist(course_id):
    course = db.session.query(chalktalk.database.Course).get(course_id)
    return render_template('createlecturelist.html', course=course)


@app.route('/feedback/<int:lecture_id>', methods=['POST', 'GET'])
@register_breadcrumb(app, '.feedbackform', 'Feedback Form', 2, endpoint_arguments_constructor=course_list_id)
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
@register_breadcrumb(app, '.feedback', 'Lecture Feedback', 3, endpoint_arguments_constructor=lecture_list_id)
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
@register_breadcrumb(app, '.addcourse', 'Add Course')
def addcourse():
    curr_user = flask_login.current_user
    # Bad way to check if the user is lecturer.
    # (Maybe use a decorator or something like that instead)
    if not hasattr(curr_user, 'lectures'):
        return redirect(url_for('index'))

    # Select all courses with no lectures added
    courses = [c for c in curr_user.courses if len(c.lectures) == 0]

    return render_template('addcourse.html', courses=courses)
