from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Length,EqualTo,Email
from flask_wtf.file import FileAllowed,FileField
from flaskblog.models import User
from flask_login import current_user









class UserRegistrationForm(FlaskForm):
    username = StringField('username',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('email', validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken, please choose another')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken, please choose another')


class UserLoginForm(FlaskForm):
    username = StringField('username',validators=[DataRequired(),Length(min=2,max=20)])
    password = PasswordField('password',validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login ')



class UserAccountForm(FlaskForm):
    username = StringField('username',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('email', validators=[DataRequired(),Email()])
    picture = FileField('Update Profile Pic',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken, please choose another')

    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken, please choose another')



class RequestResetForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(),Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email , please confirm your email or register')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Reset Password')
