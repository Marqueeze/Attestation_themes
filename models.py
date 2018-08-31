from __init__ import db
from flask_login import UserMixin
from __init__ import lm

ROLE_USER = 'user'
ROLE_TEACHER = 'teacher'
ROLE_ADMIN = 'admin'


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))



subject_attestation = db.Table('subject_attestation',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    password = db.Column(db.String(128), index = True)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.String, default = ROLE_TEACHER)

    def __repr__(self):
        return '<User '+str(self.nickname)+', role '+str(self.role)+'>'


class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    semesters = db.Column(db.String(32))
    last_change = db.Column(db.DateTime)
    allowed_users = db.Column(db.String(256))
    attestations = db.relationship("Attestation", backref = 'subject', lazy = 'dynamic')

    def __repr__(self):
        return '<Subject '+str(self.name)+'>'


class Attestation(db.Model):
    __tablename__ = 'attestation'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.SmallInteger)
    themes = db.Column(db.String, default = 'No themes yet')
    semester = db.Column(db.String(2))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    def __repr__(self):
        return '<Att '+str(Subject.query.get(self.subject_id).name)+', '+str(self.semester)+', '+str(self.number)+', '+\
               str(self.themes)+'>\r\n'
