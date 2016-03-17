import json

from flask import Blueprint
from flask import request
from flask import session
from sqlalchemy import and_
from urlparse import urlparse

from gitRoulette import auth
from gitRoulette import models
from gitRoulette.utils import request_utils


api = Blueprint('api', __name__)
db = models.db


@api.route('/add_for_review', methods=['POST'])
@auth.login_required
def add_for_review():
    if request.method == 'POST':
        req_data = json.loads(request.data)
        # FIXME: fix
        language_list = request_utils.get_url_languages(
            req_data['url'], session['github_token'][0]).keys()

        # FIXME: change name to description in post request
        # FIXME: change time to be taken on the server
        entry = models.Url(name=req_data['name'],
                           url=req_data['url'],
                           github_user=req_data['github_user'])
        for l in language_list:
            language = models.Language(language=l, url=entry)
            db.session.add(language)

        db.session.add(entry)
        db.session.commit()

    return "OK"


@api.route('/remove_from_list', methods=['POST'])
@auth.login_required
def remove_from_queue():
    req_data = json.loads(request.data)
    url = models.Url.query.filter(
        and_(models.Url.github_user == session['github_user'],
             models.Url.name == req_data['name'])).first()
    languages = url.languages.all()

    for language in languages:
        db.session.delete(language)
    db.session.delete(url)
    db.session.commit()
    return "test"


@api.route('/add_something', methods=['POST'])
@auth.login_required
def add_something():
    if request.method == 'POST':
        req_data = json.loads(request.data)

        github_user = models.GitUser.query.filter_by(
            github_user=req_data['github_user']).first()

        if github_user is not None:
            return "no user"
        # checks if user is trying to add to himself
        elif req_data['github_user'] == session['github_user']:
            return "cannot add to yourself"
        else:
            something = github_user.somethings.filter_by(
                comment_id=req_data['comment_id']).first()

        if something is None:
            something = models.Something(comment_id=req_data['comment_id'],
                                         gituser=github_user)
            db.session.add(something)
            db.session.commit()

    return "test"


@api.route('/get_something_by_url/<url_id>', methods=['GET'])
@auth.login_required
def get_something_by_url(url_id):
    # TODO: maybe we need this for something
    url = models.Url.query.filter_by(id=url_id).first()
    s = url.somethings.all()
    log(s)
    return "text"


@api.route('/get_url_languages/<url_id>', methods=['GET'])
@auth.login_required
def get_url_languages(url_id):
    url = models.Url.query.filter_by(id=url_id).first()
    languages = url.languages.all()

    language_list = [l.language for l in languages]

    ret_val = {"languages": language_list}

    return json.dumps(ret_val)


@api.route('/add_new_user', methods=['POST'])
@auth.login_required
def add_new_user():
    # TODO: modify so that a user can add/remove/replace skills;
    # TODO: case: no skills on github..
    # TODO: add a dropdown with common skills.
    if request.method == 'POST':
        req_data = json.loads(request.data)

        gituser = models.GitUser.query.filter_by(
            github_user=session['github_user']).first()

        if gituser is None:
            gituser = models.GitUser(github_user=session['github_user'])
            db.session.add(gituser)
            for skill in req_data['skills']:
                _s = models.Skill(skill=skill, gituser=gituser)
                db.session.add(_s)
            db.session.commit()
            return "success"


@api.route('/get_url_comments/<url_id>')
@auth.login_required
def get_url_comments(url_id):
    # FIXME: at the moment we only take pulls comments, no issues.
    # issues will show comments in "conversation" too.
    # Should we do another request if entry_type is pull?
    url = models.Url.query.filter_by(id=url_id).first()

    pathArray = urlparse(url.url).path.split('/')

    github_user = pathArray[1]
    project = pathArray[2]
    entry_type = pathArray[3]
    entry_id = pathArray[4]

    endpoint = 'repos/' + github_user + "/" + project + "/"
    endpoint += entry_type + "s/" + entry_id + "/comments"

    comments = auth.github.get(endpoint)

    # the response has nothing to do with the url_id restructure.
    # needs work. we need a better standard
    def lmbd(comment): comment.update({'url_name': url.name, 'url_id': url.id})
    return json.dumps(
        {project: [lmbd(comment) or comment for comment in comments.data]})


@api.route('/decline_comment', methods=['POST'])
@auth.login_required
def decline_comment():
    req_data = json.loads(request.data)
    url = models.Url.query.filter_by(id=req_data["url_id"]).first()

    pathArray = urlparse(url.url).path.split('/')
    github_user = pathArray[1]
    project = pathArray[2]
    entry_type = pathArray[3]
    entry_id = pathArray[4]

    endpoint = 'repos/' + github_user + "/" + project + "/"
    endpoint += entry_type + "s/" + entry_id + "/comments"

    post_data = {'body': 'No thanks!',
                 'in_reply_to': int(req_data["comment_id"])}
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json; charset=utf-8'}

    resp = auth.github.post(endpoint, data=post_data, headers=headers,
                            format='json')
    return json.dumps({"response": resp.data})


@api.route('/get_newuser_skills/<github_user>')
@auth.login_required
def get_newuser_skills(github_user):
    endpoint = "/users/" + github_user + "/repos"
    repos = auth.github.get(endpoint).data
    languages = [language for repo in repos for language in
                 request_utils.get_url_languages(
                    repo["html_url"], session['github_token'][0]).keys()]
    print(languages)

    return json.dumps(list(set(languages)))
