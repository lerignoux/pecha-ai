import argparse
import json
import logging

from flask import Flask, render_template, send_file, request

from flask_wtf import Form, RecaptchaField
from flask_wtf.file import FileField
from wtforms import StringField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FormField, validators

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

from presentation_generation.pptx import Pptx
from image_generation.stability import Stability
from flask_wtf.csrf import CSRFProtect

Ais = {
    'stability': Stability
}

log = logging.getLogger('peka-ai')

parser = argparse.ArgumentParser(description='Show transversal xml properties.')
parser.add_argument('--debug', '-d', dest='debug',
                    action='store_true',
                    help='Debug mode')


def get_config(ai):
    with open('config.json', 'r') as f:
        return json.load(f).get(ai)


class PechaForm(FlaskForm):
    title = StringField('presentation title', validators=[DataRequired()])
    inputs = StringField('slides ai inputs', validators=[DataRequired()])
    slide_duration = IntegerField('slides duration', validators=[DataRequired()])
    do_query = BooleanField('do query ai (billing expected)', default=False)
    ai_choice = RadioField('Ai to use', choices=[
        ('stability', 'Stability'),
        ('big_sleep', "Big Sleep"),
    ])

    recaptcha = RecaptchaField('A sample recaptcha field')
    submit_button = SubmitField('Generate Pech presentation')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'the random string'

csrf = CSRFProtect(app)

@app.before_first_request
def initialize():
    logger = logging.getLogger("peka-ai")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        """%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n%(message)s"""
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


@app.route('/', methods=['GET'])
def root():
    form = PechaForm(slide_duration=20, ai_choice="stability")
    # form.validate_on_submit()  # to get error messages to the browser
    return render_template('root.html', form=form)


@app.route('/kucha', methods=['POST', 'GET'])
def generate():
    form = MyForm()
    if not form.validate_on_submit():
        return False

    log.info(dir(form['title']))
    do_query = form['do_query'].data
    title = form['title'].data
    inputs = form['inputs'].data.split(",")
    slide_duration = form['slide_duration'].data
    ai  = request.form.get('ai', 'stability')

    images = []
    if do_query:
        log.debug(f"Generate pecha `{title}` from {inputs} using `{ai}` ai");
        images = generate_images(title, inputs, ai)
    else:
        images = default_images(title, inputs, ai)

    file = generate_pecha(title, images, slide_duration=slide_duration)
    return send_file(file, as_attachment=True)

def default_images(title, inputs, ai='stability'):
    return [
        ("fairy", "generated/test/fairy.jpg"),
        ("fish", "generated/test/fish.jpg"),
        ("cake", "generated/test/cake.jpg"),
    ]

def generate_images(title, inputs, ai='stability'):
    config = get_config(ai)
    ai = Ais[ai](title, config)
    images = []
    for input_text in inputs:
        input_text = input_text.strip()
        image = ai.generate(input_text, input_text)
        if len(image) == 0:
            raise Exception(f"Failed generating image from input {input_text}.")
        elif len(image) > 1:
            log.warning(f"multiple images generated for input {input_test}, only first image will be used.")
        images.append((title, image[0]))
    log.debug(f"Images generated: {images}")
    return images

def generate_pecha(title, images, slide_duration):
    filename = Pptx(title, slide_duration=slide_duration).generate(title, images)
    log.debug(f"Generated presentation {filename}")
    return filename


if __name__ == "__main__":
    args = parser.parse_args()
    app.run(host='0.0.0.0', port='8080', debug=True or args.debug)
