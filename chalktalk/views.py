from chalktalk import app, util
from flask import render_template, request, redirect, abort, url_for, flash
import chalktalk.database
import flask_login
from chalktalk.oauth import DataportenSignin
import re

database_url = 'sqlite:///dummy.db'
db = chalktalk.database.DatabaseManager(database_url)

app.secret_key = 'development key'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    # get will return None if not found (this is what flask_login expects)
    user = db.session.query(chalktalk.models.User).get(user_id)
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
        return redirect(url_for('lecturelist', course_id=1))
    else:
        return render_template('index.html')


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

    user = db.session.query(chalktalk.models.User).filter_by(uuid=userinfo['userid']).first()

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
            course = db.session.query(chalktalk.models.Course).filter_by(code_name=code_name).first()
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
def courselist():
    courses = db.session.query(chalktalk.database.Course).all()
    return render_template('courselist.html', courses=courses)


@app.route('/lecturelist/<int:course_id>')
@flask_login.login_required
def lecturelist(course_id):
    course = db.session.query(chalktalk.database.Course).get(course_id)
    return render_template('lecturelist.html', course=course)


@app.route('/createlecturelist/<int:course_id>', methods=['POST', 'GET'])
def createlecturelist(course_id):
    course = db.session.query(chalktalk.database.Course).get(course_id)
    return render_template('createlecturelist.html', course=course)


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

