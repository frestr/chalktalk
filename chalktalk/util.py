import re


def valid_uuid(uuid):
    return re.fullmatch('[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}', uuid) is not None


def valid_semester(semester):
    return re.fullmatch('(V|H)[1-9][0-9]{3}', semester) is not None
