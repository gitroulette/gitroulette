import os

from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from gitRoulette import auth
from gitRoulette import models
from gitRoulette.api import api
from gitRoulette.web import web


POSTGRES_HOST = 'postgres:Passw0rd@localhost'

app = Flask(__name__)
app.register_blueprint(api)
app.register_blueprint(web)

log = app.logger.debug
# TODO: handle secret_keys. This tags the session.
app.secret_key = os.urandom(24)
app.config.from_object(__name__)

# pep8... does not fit on the next row
_url = 'postgresql://' + app.config['POSTGRES_HOST'] + '/mainAPP'
app.config['SQLALCHEMY_DATABASE_URI'] = _url

db = models.db
db.init_app(app)

oauth = auth.oauth
oauth.init_app(app)


@app.before_first_request
def create_database():
    db.create_all()


@app.route('/authorized')
def authorized():
    resp = auth.github.authorized_response()
    if resp is None:
        log(request.args['error'])
        log(request.args['error_description'])
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['github_token'] = (resp['access_token'], '')
    me = auth.github.get('user')
    session['github_user'] = me.data['login']

    github_user = models.GitUser.query.filter_by(
        github_user=session['github_user']).first()

    if github_user is None:
        return redirect(url_for('web.new_user'), code=302)

    # TODO: Redirect to page where we get skills from all the repos
    #      that he has and select to add to his acc.
    #      In case no repo keep a list of skills somewhere & select from that.
    return redirect(url_for('web.index'))
    # return jsonify(me.data)


if __name__ == '__main__':
    # remove debug=True for production!
    app.run(host='0.0.0.0', port=8080, debug=True)
