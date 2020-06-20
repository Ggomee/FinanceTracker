from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DecimalField, DateField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()

        #throws validation if true if user exists
        if user:
            raise ValidationError('That username is taken. Please choose different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        # throws validation if true if user exists
        if user:
            raise ValidationError('That email is taken. Please choose different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data!=current_user.username:
            user=User.query.filter_by(username=username.data).first()

        #throws validation if true if user exists
            if user:
                raise ValidationError('That username is taken. Please choose different one.')

    def validate_email(self, email):
        if email.data!=current_user.email:
            user=User.query.filter_by(email=email.data).first()
        # throws validation if true if user exists
            if user:
                raise ValidationError('That email is taken. Please choose different one.')

class PostForm(FlaskForm):
    title=StringField('Title', validators=[DataRequired()])
    content=TextAreaField('Content', validators=[DataRequired()])

    start_year=IntegerField('Start Year', validators=[DataRequired()])
    start_month = IntegerField('Start Month', validators=[DataRequired()])
    inflation = IntegerField('Inflation', validators=[DataRequired()])
    withdrawal_rate = IntegerField('Withdrawal Rate', validators=[DataRequired()])
    start_age = IntegerField('Starting Age', validators=[DataRequired()]) # add more for use later or does that help?
    retirement_age = IntegerField('Retirement Age', validators=[DataRequired()])

    submit=SubmitField('Post')

#####need to come back to this once if figure out how this is all going to look
class DetailsForm(FlaskForm):
    category=StringField('Category', validators=[DataRequired()])
    date_entry_year=IntegerField('Entry Start Year', validators=[DataRequired()])
    date_entry_month=IntegerField('Entry Start Month', validators=[DataRequired()])
    entry_name = StringField('Entry Name', validators=[DataRequired()])
    value = IntegerField('Starting Value', validators=[DataRequired()])
    perc_change=IntegerField('Percent Change', validators=[DataRequired()])
    contrib = IntegerField('Contribution', validators=[DataRequired()])

    submit=SubmitField('Add Details')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is None:
            raise ValidationError('There is no account with that email. Please register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Reset Password')
