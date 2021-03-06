from urllib.parse import urlparse, urljoin
from flask import request
from datetime import datetime, date, timedelta
import re


def valid_uuid(uuid):
    return re.fullmatch('[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}', uuid) is not None


def valid_semester(semester):
    return re.fullmatch('(V|H)[1-9][0-9]{3}', semester) is not None


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def get_semester(group_info):
    semester_date = None
    # Means the course is active (in current semester)
    if 'notAfter' not in group_info['membership']:
        semester_date = datetime.now()
    else:
        end_date = group_info['membership']['notAfter']
        semester_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')
    year = semester_date.year
    season = 'V' if semester_date.month < 7 else 'H'
    return '{}{}'.format(season, year)

def get_lecturedates(start_date, end_date, weekday_list):
    dates = [start_date + timedelta(days=x) for x in range((end_date-start_date).days+1)]
    lecture_dates = []
    for date in dates:
        if(date.strftime("%A").lower() in weekday_list):
            lecture_dates.append(date)
    return lecture_dates
