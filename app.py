import argparse
import json
import logging

from flask import Flask, render_template, send_file, request

from flask_wtf.csrf import CSRFProtect

from pecha_form import PechaForm
from threaded_generation import threadedGeneration


log = logging.getLogger('peka-ai')


def get_config():
    with open('config.json', 'r') as f:
        return json.load(f)


app = Flask(__name__)
app.config['SECRET_KEY'] = get_config().get('flask', {}).get('secret_key', "DefaultSecretKey")
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
    return render_template('root.html', form=form)


@app.route('/pecha', methods=['POST', 'GET'])
async def generate():
    form = PechaForm(slide_duration=20, ai_choice="stability")

    title = form['title'].data
    if title == "__default__":
        raise Exception("Reserved title.")
    inputs = form['inputs'].data.split("\n")
    slide_duration = form['slide_duration'].data
    ai  = request.form.get('ai_choice', 'stability')

    log.debug(f"Generate pecha `{title}` from {inputs} using `{ai}` ai");

    generator = threadedGeneration(get_config())
    images = generator.generate_images(title, inputs, ai)
    file = generator.generate_pecha(title, images, slide_duration=slide_duration)
    return send_file(file, as_attachment=True)


if __name__ == "__main__":
    debug = get_config().get('flask', {}).get('debug', False)
    app.run(host='0.0.0.0', port='8080', debug=debug)
