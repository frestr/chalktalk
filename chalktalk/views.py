from chalktalk import app, util
from flask import render_template, request, redirect, abort, url_for, flash
import chalktalk.database
import flask_login
from chalktalk.oauth import DataportenSignin
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
import re
from chalktalk.models import User, Course
from datetime import datetime, date
from chalktalk import settings, secret_settings

db = chalktalk.database.DatabaseManager(settings.DATABASE_URL)

app.secret_key = secret_settings.SECRET_KEY

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
        return render_template('index.html', debugging=app.debug)


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
            role = group['membership']['fsroles'][0]
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
    curr_user = flask_login.current_user.type
    courses = flask_login.current_user.courses
    return render_template('courselist.html', courses=courses, user=curr_user)


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
    curr_user = flask_login.current_user.type
    course = db.session.query(chalktalk.database.Course).get(course_id)
    if course:
        return render_template('lecturelist.html', course=course, user=curr_user)
    return redirect(url_for('courselist'))


@app.route('/createlecturelist/<int:course_id>', methods=['POST'])
@register_breadcrumb(app, '.createcourse', 'Create Lecture List', 1, endpoint_arguments_constructor=course_list_id)
@flask_login.login_required
def createlecturelist(course_id):
    if flask_login.current_user.type != 'lecturer':
        abort(403)

    course = db.session.query(Course).get(course_id)
    if course:
        tags_list = []
        for entry in request.form:
            match = re.fullmatch('([0-9]+)_tags', entry)
            if match:
                lecture_date = request.form['{}_date'.format(match.group(1))]
                lecture_date = datetime.strptime(lecture_date, '%Y-%m-%d %H:%M:%S')
                tags_list.append((match.group(0), lecture_date, request.form[entry]))

        for tags in sorted(tags_list, key=lambda x: x[0]):
            lecture_date = tags[1]
            lecture = db.add_lecture(course, lecture_date, 'MTDT', [flask_login.current_user])
            # CHECK IF THE TAGS ARE PROPERLY FORMATTED HERE
            for tag in tags[2].split(','):
                db.add_subject(lecture, tag.strip())

        db.save_changes()

    else:
        print('Course does not exist: {}'.format(course_id))
        abort(400)
    return redirect(url_for('index'))


@app.route('/feedback/<int:lecture_id>', methods=['POST', 'GET'])
@register_breadcrumb(app, '.feedbackform', 'Feedback Form', 2, endpoint_arguments_constructor=lecture_list_id)
@flask_login.login_required
def feedbackform(lecture_id):
    if flask_login.current_user.type != 'student':
        abort(403)

    lecture = db.session.query(chalktalk.database.Lecture).get(lecture_id)

    ##### NB : This should be the student giving the feedback, not just a 
    ##### random student like now (just for testing)
    student = flask_login.current_user
    #####

    if lecture is None:
        print('Lecture does not exist: {}'.format(lecture_id))
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
@flask_login.login_required
def lecturefeedback(lecture_id):
    if flask_login.current_user.type != 'lecturer':
        abort(403)

    lecture = db.session.query(chalktalk.database.Lecture).filter_by(id=lecture_id).first()
    if lecture is None:
        print('Lecture does not exist: {}'.format(lecture_id))
        abort(404)
    subjects = db.get_subject_values(lecture)
    return render_template('lecturefeedback.html', subjects=subjects, lecture=lecture)


@app.route('/semesteroverview/<int:course_id>')
@flask_login.login_required
def semesteroverview(course_id):
    course = db.session.query(chalktalk.database.Course).get(course_id)
    lectures = []
    labels = []
    lecture_id = 1
    # get all of the lectures from the course
    for lecture in course.lectures:
        labels.append(lecture_id)
        lectures.append(db.session.query(chalktalk.database.Lecture).filter_by(id=lecture.id).first())
        lecture_id += 1
    subjects = []
    for lecture in lectures:
        subjects.append(db.get_subject_values(lecture))
    # getting individual rating
    feedback = []
    for i in range(len(subjects)):
        rating_sum = 0
        for j in range(len(subjects[i])):
            for k in range(len(subjects[i][j]['comments'])):
                rating_sum += subjects[i][j]['comments'][k][0]

            #if (len(subjects[i][j]['comments']) != 0):
            #   labels.append(str(subjects[i][j]['name']))
        #feedback.append(rating_sum)

    #print(feedback)

    for lecture in lectures:
        rating_sum = 0
        rating_count = 0
        for subject in lecture.subjects:
            for rating_feedback in subject.feedbacks:
                rating_sum += rating_feedback.comprehension_rating
                rating_count += 1
        #print("----->" + str(rating_sum) + " " + str(rating_count))
        if rating_count == 0:
            feedback.append(rating_sum/1)
        else:
            feedback.append(rating_sum/rating_count)
    """
    for i in range(len(ratings)):
        res = 0
        for j in range(len(ratings[i])):
            res += ratings[i][j]
        feedback.append(res)
    """

    if flask_login.current_user.type != 'lecturer':
        abort(403)

    return render_template('semesteroverview.html', course=course, feedback=feedback, label=labels, subjects=subjects)

@app.route('/addcourse', methods=['GET', 'POST'])
@register_breadcrumb(app, '.addcourse', 'Add Course')
@flask_login.login_required
def addcourse():
    if flask_login.current_user.type != 'lecturer':
        abort(403)

    if request.method == 'POST':
        course_code = request.form['course_code']
        course = db.session.query(Course).filter_by(code_name=course_code).first()
        if not course:
            print('Course does not exist: {}'.format(course_code))
            abort(400)

        from_date_str = request.form['from_date']
        to_date_str = request.form['to_date']

        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
        except ValueError:
            print('Invalid date formats: {} or {}'.format(from_date, to_date))
            abort(400)

        days = []
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            if day in request.form and request.form[day] == 'on':
                days.append(day)
                # from_hours = request.form['{}_hours_from'.format(day)]
                # from_minutes = request.form['{}_minutes_from'.format(day)]
                # to_hours = request.form['{}_hours_to'.format(day)]
                # to_minutes = request.form['{}_minutes_to'.format(day)]

        dates = util.get_lecturedates(from_date, to_date, days)
        return render_template('createlecturelist.html', course=course, dates=dates)

    # Select all courses with no lectures added
    courses = [c for c in flask_login.current_user.courses if len(c.lectures) == 0]

    return render_template('addcourse.html', courses=courses)

@app.route('/editlecturetags/<int:course_id>', methods=['GET', 'POST'])
@flask_login.login_required
def editlecturetags(course_id):
    if flask_login.current_user.type != 'lecturer':
        abort(403)

    course = db.session.query(chalktalk.database.Course).get(course_id)
    if request.method == 'POST':

        tags_list = []
        for entry in request.form:
            match = re.fullmatch('([0-9]+)_tags', entry)
            if match:
                lecture_date = request.form['{}_date'.format(match.group(1))]
                lecture_date = datetime.strptime(lecture_date, '%Y-%m-%d %H:%M:%S')
                tags_list.append((match.group(0), lecture_date, request.form[entry]))

        for tags in sorted(tags_list, key=lambda x: x[0]):
            lecture_date = tags[1]
            lecture = db.add_lecture(course, lecture_date, 'MTDT', [flask_login.current_user])
            # CHECK IF THE TAGS ARE PROPERLY FORMATTED HERE
            for tag in tags[2].split(','):
                db.add_subject(lecture, tag.strip())

        db.save_changes()

    lecture_tags = []
    for lecture in course.lectures:
        tags = ""
        for subject in lecture.subjects:
            tags += subject.keyword + ", "
        lecture_tags.append(tags)
        print(lecture_tags)

    return render_template('editlecturetags.html', lectures=course.lectures, course=course, tags=lecture_tags)
