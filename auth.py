import os

from flask import redirect
from flask import url_for
from flask import session
from functools import wraps

from flask_oauthlib.client import OAuth


# oauth for github connections
oauth = OAuth()
github = oauth.remote_app(
    'github',
    consumer_key=os.getenv('CLIENT_ID'),
    consumer_secret=os.getenv('CLIENT_SECRET'),
    request_token_params={'scope': 'user:email,public_repo,notifications'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token', None)


def login_required(f):
    # TODO: Keep in g, not in session? Make thread safe.
    #       He might not be able to get to github, but can he touch our stuff?
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'github_token' not in session:
            return redirect(url_for('web.login'))
        else:
            try:
                github.get('user')
            except ValueError as e:
                # Check the message/code to see if we have the case we want:
                # "Missing access token."
                return redirect(url_for('web.login'))
        return f(*args, **kwargs)
    return decorated_function
