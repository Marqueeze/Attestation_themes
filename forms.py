from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, AnyOf, Regexp


class LoginForm(Form):
    login = StringField('login', validators = [DataRequired()])
    password = PasswordField('password', validators = [DataRequired()])


class SubjectForm(Form):
    name = StringField('name', validators=[DataRequired()])
    semesters = StringField('semesters', validators=[DataRequired(), Regexp('([0-8], )*[0-8]')])
    allowed_users = StringField('allowed_users')
    create = BooleanField('create', default = False)


class RefactorForm(Form):
    att1 = TextAreaField('att1')
    att2 = TextAreaField('att2')
    att3 = TextAreaField('att3')
    users_to_add = StringField('users_to_add')
    users_to_delete = StringField('users_to_delete')


class RegisterForm(Form):
    login = StringField('login', validators=[DataRequired(), Length(min=4)])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8)])
    double_password = PasswordField('double_password', validators=[
        DataRequired(),
        EqualTo('password', "Passwords are different"),
        Length(min=8)
    ]
    )
    special_password = PasswordField('special-password')
