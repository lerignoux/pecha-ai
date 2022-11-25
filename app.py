import argparse
import json
import logging

from flask import Flask, render_template, send_file, request, abort

from flask_wtf.csrf import CSRFProtect

from pecha_form import PechaForm
from threaded_generation import threadedGeneration, GenerationException


log = logging.getLogger('peka-ai')


def get_config():
    with open('config.json', 'r') as f:
        return json.load(f)


app = Flask(__name__)
app.config['SECRET_KEY'] = get_config().get('flask', {}).get('secret_key', "DefaultSecretKey")
csrf = CSRFProtect(app)


def data_size(directory = "./generated/"):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def oldest_directory(directory = "./generated/"):
    oldest = None
    for folder in os.listdir(directory):

        if not os.path.isdir(directories):
            continue

        if oldest is None or os.stat(folder).st_ctime < os.stat(oldest).st_ctime:
            oldest = folder

    return oldest


def delete_oldest(directory = "./generated/"):
    oldest = oldest_directory(directory)
    log.info(f"sudo rm -rf {oldest}")
    # os.system(f"sudo rm -rf {oldest}")


def clean_data():
    max_size = get_config().get("data_size", 50)
    while data_size() > max_size:
        delete_oldest("./generated/")


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

    clean_data()

@app.route('/', methods=['GET'])
def root():
    form = PechaForm(slide_duration=20, ai_choice="stability")
    return render_template('root.html', form=form)


@app.route('/pecha', methods=['POST'])
async def generate():
    form = PechaForm(slide_duration=20, ai_choice="stability")

    title = form['title'].data
    inputs = form['inputs'].data.split("\n")
    slide_duration = form['slide_duration'].data
    ai  = request.form.get('ai_choice', 'stability')

    log.debug(f"Generate pecha `{title}` from {inputs} using `{ai}` ai");

    generator = threadedGeneration(get_config())
    try:
        images = generator.generate_images(title, inputs, ai)
    except GenerationException as e:
        abort(500, str(e))
    file = generator.generate_pecha(title, images, slide_duration=slide_duration)
    return send_file(file, as_attachment=True)


if __name__ == "__main__":
    debug = get_config().get('flask', {}).get('debug', False)
    app.run(host='0.0.0.0', port='8080', debug=debug)
