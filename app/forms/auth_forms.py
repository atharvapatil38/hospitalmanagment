from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Update Password')

class UserProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    submit = SubmitField('Save Changes')

class UserAdminForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    role_id = SelectField('User Role', coerce=int, validators=[DataRequired()])
    password = PasswordField('Password (leave blank to keep current)')
    is_active = BooleanField('Account Active', default=True)
    submit = SubmitField('Save User')
