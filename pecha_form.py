import logging

from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField
from wtforms import StringField, RadioField, SubmitField, IntegerField, TextAreaField, validators
from wtforms.validators import DataRequired, Length, NoneOf

log = logging.getLogger(__name__)


class PechaForm(FlaskForm):
    default_inputs = [
        "A dead tree photo on a hill",
        "A view from space of hearth with volcano erupting",
        "A dark painting of a nightsky signed \"Questions\""
    ]

    title = StringField(
        'presentation title',
        validators=[DataRequired(), Length(max=64), NoneOf("__default__")],
        render_kw={"placeholder": "presentation title"}
    )

    inputs_placeholder = "input each slide ai text input per line, for instance\n" + "\n".join(default_inputs)
    inputs = TextAreaField(
        'slides ai inputs',
        validators=[DataRequired()],
        render_kw={"placeholder": inputs_placeholder}
    )

    slide_duration = IntegerField('slides duration', validators=[DataRequired()])
    ai_choice = RadioField('Ai model', choices=[
        ('none', 'None: Test'),
        ('stability', 'Stability')
    ])

    recaptcha = RecaptchaField('A sample recaptcha field')
    submit_button = SubmitField('Generate Pech presentation')

