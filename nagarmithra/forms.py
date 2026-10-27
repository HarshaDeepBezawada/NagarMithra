"""
NagarMitra Forms
=================
WTForms form classes for complaint submission and admin interactions.
Server-side validation ensures data integrity regardless of browser behavior.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, SelectField, PasswordField, SubmitField,
)
from wtforms.validators import DataRequired, Length, Optional

from nagarmithra.models import CATEGORIES, PRIORITIES, STATUSES


class ComplaintForm(FlaskForm):
    """
    Form for citizens to submit a new complaint.

    All fields are validated server-side. The image upload is optional
    but restricted to safe image formats and a maximum file size.
    """
    citizen_name = StringField('Your Name', validators=[
        DataRequired(message='Please enter your name.'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters.'),
    ])
    citizen_contact = StringField('Contact (Phone or Email)', validators=[
        DataRequired(message='Please provide a phone number or email.'),
        Length(min=5, max=100, message='Contact must be between 5 and 100 characters.'),
    ])
    title = StringField('Complaint Title', validators=[
        DataRequired(message='Please provide a brief title.'),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters.'),
    ])
    description = TextAreaField('Detailed Description', validators=[
        DataRequired(message='Please describe the issue in detail.'),
        Length(min=20, max=5000, message='Description must be between 20 and 5000 characters.'),
    ])
    category = SelectField('Issue Category', choices=[('', '-- Select Category --')] + CATEGORIES,
                           validators=[DataRequired(message='Please select a category.')])
    priority = SelectField('Priority Level', choices=PRIORITIES,
                           validators=[DataRequired()])
    location = StringField('Location / Address', validators=[
        DataRequired(message='Please provide the location of the issue.'),
        Length(min=5, max=300, message='Location must be between 5 and 300 characters.'),
    ])
    image = FileField('Upload Photo (optional)', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'webp'], 'Only image files are allowed.'),
        Optional(),
    ])
    submit = SubmitField('Submit Complaint')


class TrackingForm(FlaskForm):
    """Form for citizens to look up a complaint by its reference number."""
    reference = StringField('Complaint Reference Number', validators=[
        DataRequired(message='Please enter your complaint reference number.'),
        Length(min=5, max=20, message='Reference number appears invalid.'),
    ])
    submit = SubmitField('Track Complaint')


class LoginForm(FlaskForm):
    """Administrator login form."""
    username = StringField('Username', validators=[
        DataRequired(message='Please enter your username.'),
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Please enter your password.'),
    ])
    submit = SubmitField('Sign In')


class StatusUpdateForm(FlaskForm):
    """Form for administrators to update a complaint's status."""
    status = SelectField('New Status', choices=STATUSES,
                         validators=[DataRequired()])
    priority = SelectField('Priority', choices=PRIORITIES,
                           validators=[DataRequired()])
    admin_notes = TextAreaField('Admin Notes / Resolution Details', validators=[
        Optional(),
        Length(max=2000),
    ])
    submit = SubmitField('Update Complaint')
