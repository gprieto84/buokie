from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, InputRequired, Length
from appdir import db



class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Please enter the username'),Length(min=5,max=12)])
    email = StringField('Email', validators=[DataRequired('Please enter the email'), Email('Not a valid Email')])
    first_name =  StringField('First name', validators=[DataRequired('Please enter your first name')])
    last_name =  StringField('Last name', validators=[DataRequired('Please enter your last name')])
    password = PasswordField('Password', validators=[DataRequired('Please enter the password'), Length(min=8,max=25)])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired('Please enter the password'), Length(min=8, max=25),
     EqualTo('password','Password Mismatch')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = db.execute('SELECT 1 FROM users WHERE email=:email',{"email":email.data}).fetchone()
        if user is not None:
            raise ValidationError('This email is already taken')
    
    def validate_username(self, username):
        user = db.execute('SELECT 1 FROM users WHERE username=:username',{"username":username.data}).fetchone()
        if user is not None:
            raise ValidationError('This username is already taken')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Please enter the username'),Length(min=5,max=12)])
    password = PasswordField('Password', validators=[DataRequired('Please enter the password'), Length(min=8,max=25)])
    submit = SubmitField('Sign in')

class SearchForm(FlaskForm):
    search = StringField('', validators=[DataRequired('Please enter some text'),Length(min=2,max=60)])
    submit = SubmitField('Search')

class ReviewForm(FlaskForm):
    star = SelectField('Rating:', coerce=int, validators=[InputRequired('Please select a rating')], choices=[(1, '1 star'), (2, '2 star'), (3, '3 star'), (4, '4 star'), (5, '5 star')])
    review = StringField('Review', widget=TextArea(), validators=[Length(max=100)])
    submit = SubmitField('Send Review')