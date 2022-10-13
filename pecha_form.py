import logging

from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField
from wtforms import StringField, RadioField, SubmitField, IntegerField, TextAreaField, validators
from wtforms.validators import DataRequired, Length, NoneOf

log = logging.getLogger(__name__)


class PechaForm(FlaskForm):
    title = StringField(
    	'presentation title',
    	validators=[DataRequired(), Length(max=64), NoneOf("__default__")],
    	render_kw={"placeholder": "presentation title"}
    )
    inputs = TextAreaField(
    	'slides ai inputs',
    	validators=[DataRequired()],
    	render_kw={"placeholder": "input each slide ai text input per line"}
    )
    slide_duration = IntegerField('slides duration', validators=[DataRequired()])
    ai_choice = RadioField('Ai to use', choices=[
        ('none', 'None'),
        ('stability', 'Stability')
    ])

    recaptcha = RecaptchaField('A sample recaptcha field')
    submit_button = SubmitField('Generate Pech presentation')

