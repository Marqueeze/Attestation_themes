from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from forms import LoginForm, RegisterForm, SubjectForm, RefactorForm
from models import *
from config import TEACHER_PASSWORD, ADMIN_PASSWORD
import datetime
from __init__ import app, db
import re


@app.before_request
def before_request():
    g.user = current_user


@app.route('/create', methods = ["GET","POST"])
@login_required
def create():
    user = g.user
    subjectform = SubjectForm()
    if subjectform.validate_on_submit():
        if (g.user.role == ROLE_TEACHER) | (g.user.role == ROLE_ADMIN):
            sems = re.findall('\d+', subjectform.semesters.data)
            commit_subject = Subject(name=subjectform.name.data.lower(), semesters=subjectform.semesters.data,
                                     allowed_users="{0} {1}".format(str(g.user.nickname),
                                            re.sub('\W+', ' ', subjectform.allowed_users.data.lower())),
                                     last_change=datetime.datetime.now())
            db.session.add(commit_subject)
            for semester in sems:
                for i in range(3):
                    commit_att = Attestation(number=i + 1, semester=semester,
                                             subject_id=commit_subject.id, subject=commit_subject)
                    db.session.add(commit_att)
            db.session.commit()
            flash('Added successfully')
            return redirect(url_for('subjectpage', name=commit_subject.name, semester=sems[0]))
        else:
            flash('No permission to create subjects')
    return render_template("create.html", form=subjectform, user=user)


@app.route('/', methods = ["GET","POST"])
@app.route('/find', methods = ["GET", "POST"])
@login_required
def find():
    user = g.user
    subjectform = SubjectForm()
    if subjectform.validate_on_submit():
        semtmp = re.search('^\d+', subjectform.semesters.data).group(0)
        subjects = list(filter(lambda x: semtmp in x.semesters,
                      Subject.query.filter_by(name = subjectform.name.data.lower())))
        if len(subjects) != 0:
            if subjects[0] is not None:
                return redirect(url_for('subjectpage', name = subjects[0].name, semester = semtmp))
        flash("No subject with this parameters")
        subjectform.name.data = ""
        subjectform.semesters.data = ""
    return render_template("find.html", form = subjectform, user = user)


@app.route('/subjects/<name>/<semester>', methods = ["GET", "POST"])
@login_required
def subjectpage(name, semester):
    subject = Subject.query.filter_by(name=name).first()
    if subject is not None:
        themes = [x.themes for x in list(Attestation.query.filter_by(subject_id = subject.id, semester = semester))]
        if len(themes) != 0:
            return render_template('subjects.html', themes = themes, user = g.user, name = name, semester = semester)
    flash('No subjects with such parameters')
    return redirect(url_for('find'))


@app.route('/refactor_subjects/<name>/<semester>', methods = ["GET", "POST"])
@login_required
def refactor(name, semester):
    subject = Subject.query.filter_by(name=name).first()
    if subject is not None and semester in subject.semesters:
        if (g.user.role == ROLE_ADMIN) | (g.user.nickname in subject.allowed_users):
            ref_form = RefactorForm()
            subj_form = SubjectForm()
            att_number = {1: ref_form.att1,
                          2: ref_form.att2,
                          3: ref_form.att3}
            if ref_form.validate_on_submit():
                for att in subject.attestations:
                    if att.semester == semester:
                        att.themes = att_number[att.number].data
                subject.last_change = datetime.datetime.now()
                subject.allowed_users += ' '+ref_form.users_to_add.data.lower()
                for nick in ref_form.users_to_delete.data.lower().split(' '):
                    subject.allowed_users = subject.allowed_users.replace(nick, "").rstrip()
                subject.name = subj_form.name.data.lower()
                subject.semesters = subj_form.semesters.data.lower()
                db.session.add(subject)
                db.session.commit()
                return redirect(url_for('subjectpage', name = subject.name, semester = semester))
            else:
                subj_form.name.data = str(subject.name)
                subj_form.semesters.data = str(subject.semesters)
                for att in subject.attestations:
                    if att.semester == semester:
                        att_number[att.number].data = att.themes
                return render_template('refactor.html', subject=subject, user=g.user, semester=semester,
                                       ref_form = ref_form, subj_form = subj_form)
        else:
            flash('No permission to change themes')
            return redirect(url_for('subjects.html', subject=subject, user=g.user, semester=semester))
    else:
        flash('No subjects with such parameters')
        return redirect(url_for('find'))


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for("find"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.login.data.lower()).first()
        if user is None:
            flash("No user with such nickname")
            return redirect(url_for("login"))
        if form.password.data == user.password:
            login_user(user)
            return redirect(request.args.get('next') or url_for('find'))
        else:
            flash('Wrong password')
    return render_template('login.html', title = 'Sign In', form = form)


@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname = form.login.data.lower()).first()
        if user is None:
            role = ROLE_USER
            if form.special_password.data == TEACHER_PASSWORD:
                role = ROLE_TEACHER
            if form.special_password.data == ADMIN_PASSWORD:
                role = ROLE_ADMIN
            if form.special_password.data and role == ROLE_USER:
                flash('WRONG SPECIAL PASSWORD')
                return redirect(url_for('register'))
            user = User(nickname = form.login.data.lower(), email = form.email.data.lower(),
                        password = form.password.data, role = role.lower())
            db.session.add(user)
            db.session.commit()
            flash('Registred succesfully')
            return redirect(request.args.get('next') or url_for('login'))
        flash('Nickname is not available')
    return render_template("register.html", form = form)


@app.route('/personal', methods = ["GET","POST"])
@login_required


def personal_data():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.login.data.lower()).first()
        if user is None:
            role = ROLE_USER
            if form.special_password.data == TEACHER_PASSWORD:
                role = ROLE_TEACHER
            if form.special_password.data == ADMIN_PASSWORD:
                role = ROLE_ADMIN
            if form.special_password.data and role == ROLE_USER:
                flash('WRONG SPECIAL PASSWORD')
                return redirect(url_for('personal_data'))
            user = User(nickname=form.login.data.lower(), email=form.email.data.lower(), role=role.lower())
            db.session.add(user)
            db.session.commit()
            flash('Registred succesfully')
            return redirect(request.args.get('next') or url_for('login'))
        flash('Nickname is not available')
    else:
        form.login.data = str(g.user.nickname)
        form.email.data = str(g.user.email)
        form.special_password.data = ''
    return render_template("personal_data.html", form=form)


@app.route('/password_changer', methods = ["GET", "POST"])
@login_required
def password_changer():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.special_password.data == str(g.user.password):
            if str(form.password.data) == str(form.double_password.data):
                db.session.delete(g.user)
                g.user.password = str(form.password.data)
                db.session.add(g.user)
                db.session.commit()
                flash('Changed successfully')
                return redirect(url_for('find'))
            else:
                flash("Passwords are not equal")
        else:
            flash("Wrong current password")
    return render_template('password_changer.html', form = form, user = g.user)


def Clear_DB():
    for u in User.query.all():
        db.session.delete(u)
    for s in Subject.query.all():
        db.session.delete(s)
    db.session.commit()


if __name__ == '__main__':
    print(User.query.all())
    print(Subject.query.all())
    print(Attestation.query.all())
    #Clear_DB()
    app.run(debug = True)
