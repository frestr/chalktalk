from rauth import OAuth2Service
from flask import url_for, request, redirect
from chalktalk import secret_settings
import json

"""
Methods for using Feide to sign in.
"""

class DataportenSignin():
    def __init__(self):
        self.service = OAuth2Service(
            name='dataporten',
            client_id=secret_settings.OAUTH_CREDENTIALS['id'],
            client_secret=secret_settings.OAUTH_CREDENTIALS['secret'],
            authorize_url='https://auth.dataporten.no/oauth/authorization',
            access_token_url='https://auth.dataporten.no/oauth/token',
            base_url='https://auth.dataporten.no/'
        )

    def get_callback_url(self):
        return url_for('oauth_callback', _external=True)

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='userid profile groups',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None
        try:
            oauth_session = self.service.get_auth_session(
                data={'code': request.args['code'],
                      'grant_type': 'authorization_code',
                      'redirect_uri': self.get_callback_url()},
                decoder=lambda x: json.loads(x.decode())
            )
        except KeyError:
            return None, None
        userinfo = oauth_session.get('userinfo').json()
        groups = oauth_session.get('https://groups-api.dataporten.no/groups/me/groups').json()
        if ('user' in userinfo and
                    'name' in userinfo['user'] and
                    'userid' in userinfo['user']):
            return userinfo['user'], groups
        return None, None
