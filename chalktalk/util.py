from urllib.parse import urlparse, urljoin
from flask import request
from datetime import datetime
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
    date = None
    # Means the course is active (in current semester)
    if 'notAfter' not in group_info['membership']:
        date = datetime.now()
    else:
        end_date = group_info['membership']['notAfter']
        date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')
    year = date.year
    season = 'V' if date.month < 7 else 'H'
    return '{}{}'.format(season, year)
