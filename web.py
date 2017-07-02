from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for
from flask import session

from gitRoulette import auth


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
    return render_template("index.html")


@web.route('/new_user', methods=['GET'])
@auth.login_required
def new_user():
    return render_template("newUser.html")
