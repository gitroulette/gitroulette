import json

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for
from flask import session

from gitRoulette import auth
from gitRoulette import models


web = Blueprint('web', __name__)


@web.route('/login')
def login():
    return auth.github.authorize(callback=url_for('authorized',
                                                  _external=True))


@web.route('/logout')
@auth.login_required
def logout():
    session.pop('github_token')
    session.pop('github_user')
    return redirect(url_for('web.index'))


@web.route('/', methods=['GET'])
@auth.login_required
def index():
    urls = models.Url.query.filter_by(github_user=session['github_user']).all()
    existing_urls = []
    for url in urls:
        entry = {'id': url.id,
                 'name': url.name,
                 'url': url.url,
                 'github_user': url.github_user}
        existing_urls.append(entry)

    return render_template("index.html", existing=json.dumps(existing_urls))


@web.route('/new_user', methods=['GET'])
@auth.login_required
def new_user():
    return render_template("newUser.html")
