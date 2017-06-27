import json
import random

from flask import Blueprint
from flask import request
from flask import session
from sqlalchemy import and_
from sqlalchemy import or_
from urlparse import urlparse
# from flask import current_app

from gitRoulette import auth
from gitRoulette import models
from gitRoulette.utils import request_utils


api = Blueprint('api', __name__)
db = models.db


@api.route('/new_for_review', methods=['POST'])
@auth.login_required
def new_for_review():
    if request.method == 'POST':
        req_data = json.loads(request.data)

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

    return str(entry.id)


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


@api.route('/new_something', methods=['POST'])
@auth.login_required
def new_something():
    if request.method == 'POST':
        req_data = json.loads(request.data)

        github_user = models.GitUser.query.filter_by(
            github_user=req_data['github_user']).first()

        if github_user is None:
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


@api.route('/somethings_by_url_id/<url_id>', methods=['GET'])
@auth.login_required
def somethings_by_url_id(url_id):
    # TODO: maybe we need this for something
    url = models.Url.query.filter_by(id=url_id).first()
    somethings = [s.comment_id for s in url.somethings.all()]
    return json.dumps({"somethings": somethings})


@api.route('/somethings_by_username/<username>', methods=['GET'])
@auth.login_required
def somethings_by_username(username):
    github_user = models.GitUser.query.filter_by(github_user=username).first()
    somethings = [s.comment_id for s in github_user.somethings.all()]
    print(somethings)
    return json.dumps({"somethings": somethings})


@api.route('/languages_by_url_id/<url_id>', methods=['GET'])
@auth.login_required
def languages_by_url_id(url_id):
    url = models.Url.query.filter_by(id=url_id).first()
    languages = url.languages.all()

    language_list = [l.language for l in languages]

    ret_val = {"languages": language_list}

    return json.dumps(ret_val)


@api.route('/new_github_user', methods=['POST'])
@auth.login_required
def new_github_user():
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


@api.route('/comments_by_url_id/<url_id>')
@auth.login_required
def comments_by_url_id(url_id):
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


@api.route('/skills_by_username/<github_user>', methods=['GET'])
@auth.login_required
def skills_by_username(github_user):
    endpoint = "/users/" + github_user + "/repos"
    repos = auth.github.get(endpoint).data
    languages = [language for repo in repos for language in
                 request_utils.get_url_languages(
                    repo["html_url"], session['github_token'][0]).keys()]
    print(languages)

    return json.dumps(list(set(languages)))


@api.route('/saved_skills_by_username/<github_user>', methods=['GET'])
@auth.login_required
def saved_skills_by_username(github_user):

    user = models.GitUser.query.filter_by(github_user=github_user).first()
    skills = user.skills.all()
    skills_list = [s.skill for s in skills]

    return json.dumps(list(set(skills_list)))


@api.route('/urls_by_username/<github_user>', methods=['GET'])
@auth.login_required
def saved_urls_by_username(github_user):

    urls = models.Url.query.filter_by(github_user=github_user).all()
    existing_urls = []
    for url in urls:
        entry = {'id': url.id,
                 'name': url.name,
                 'url': url.url,
                 'github_user': url.github_user}
        existing_urls.append(entry)

    return json.dumps(existing_urls)


@api.route('/url_to_review', methods=['GET'])
@auth.login_required
def url_to_review():

    user = models.GitUser.query.filter_by(github_user=session['github_user']).first()
    skills = user.skills.all()

    # We need to have atleast one condition otherwise the query will return all.
    if len(skills) == 0:
        return ''

    conditions = [getattr(models.Language, 'language').ilike('%{}%'.format(s.skill)) for s in skills]

    q = models.Language.query.filter(or_(*conditions)).distinct(models.Language.url_id)
    language_entries = q.all()
    random_url_id = random.choice(language_entries).url_id
    url = models.Url.query.filter_by(id=random_url_id).first()

    return str(url.url)