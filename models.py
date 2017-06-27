from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import text


db = SQLAlchemy()


class Url(db.Model):
    __tablename__ = 'url'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    url = db.Column(db.String())
    github_user = db.Column(db.String())
    created = db.Column(db.DateTime, server_default=text('now()'))
    languages = db.relationship('Language', backref='url', lazy='dynamic')
    # somethings = db.relationship('Something', backref='url', lazy='dynamic')

    def __init__(self, name, url, github_user):
        self.name = name
        self.url = url
        self.github_user = github_user

    def __repr__(self):
        val = "<Url(url='%s', name='%s', github_user='%s', created='%s')>"
        return val % (self.url, self.name, self.github_user, self.created)


class Language(db.Model):
    __tablename__ = 'language'

    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(30))
    url_id = db.Column(db.Integer, db.ForeignKey('url.id'))


class GitUser(db.Model):
    __tablename__ = 'gituser'

    id = db.Column(db.Integer, primary_key=True)
    github_user = db.Column(db.String())
    skills = db.relationship('Skill', backref='gituser',
                             lazy='dynamic')
    achievements = db.relationship('Achievement', backref='gituser',
                                   lazy='dynamic')
    somethings = db.relationship('Something', backref='gituser',
                                 lazy='dynamic')

    def __init__(self, github_user):
        self.github_user = github_user

    def __repr__(self):
        val = "<GitUser(github_user='%s', skills='%s', " + \
            "achievements='%s', somethings='%s')>"
        return val % (self.github_user, self.skills, self.achievements,
                      self.somethings)


class Skill(db.Model):
    __tablename__ = 'skill'

    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.String(30))
    person_id = db.Column(db.Integer, db.ForeignKey('gituser.id'))


class Achievement(db.Model):
    __tablename__ = 'achievement'

    id = db.Column(db.Integer, primary_key=True)
    achievement = db.Column(db.String())
    person_id = db.Column(db.Integer, db.ForeignKey('gituser.id'))


class Something(db.Model):
    __tablename__ = 'something'

    id = db.Column(db.Integer, primary_key=True)
    # url_ref = db.Column(db.Integer, db.ForeignKey('url.id'))
    comment_id = db.Column(db.String(15))
    person_id = db.Column(db.Integer, db.ForeignKey('gituser.id'))
