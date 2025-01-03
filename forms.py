from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import Length, DataRequired, ValidationError
from models import User


class register_form(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    username = StringField(label='UserName:', validators=[Length(min=2, max=30), DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=2), DataRequired()])
    submit = SubmitField(label='Create Account')


class login_form(FlaskForm):
    username = StringField(label='UserName:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')





class delete_form(FlaskForm):
    delete = SubmitField(label='Delete')


class admin_edit_user_form(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    is_admin = RadioField('Is Admin?', choices=[('True', 'Yes'), ('False', 'No')], default='False', validators=[DataRequired()])
    submit = SubmitField(label='Update User')






class admin_delete_user_form(FlaskForm):
    delete = SubmitField(label='Delete User')






