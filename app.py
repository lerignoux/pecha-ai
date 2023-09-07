import argparse
import json
import logging
import os
import pathlib

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
    data_path = os.path.join(pathlib.Path().resolve(), directory)
    for folder in os.listdir(data_path):
        if folder == "__default__" or not folder:
            continue

        folder_path = os.path.join(data_path, folder)

        if not os.path.isdir(folder_path):
            continue

        if oldest is None or os.stat(oldest).st_ctime > os.stat(folder_path).st_ctime:
            oldest = folder_path

    return oldest


def delete_oldest(directory = "./generated/"):
    oldest = oldest_directory(directory)
    if oldest is not None:
        oldest = oldest.replace(" ", "\\ ").replace("(", "\\(").replace(")", "\\)")
        log.debug(f"removing oldest folder {oldest}")
        os.system(f"rm -rf {oldest}")
    else:
        log.debug("No oldest folder to delete.")


def clean_data():
    """
    Remove oldest ressources if generated data exceed 50 Mo
    """
    max_size = get_config().get("data_size", 50000000)
    while data_size() > max_size:
        old_size = data_size()
        delete_oldest("./generated/")
        if data_size() == old_size:
            log.warning(f"Could not free space before request. app may take more than 50M. current storage: {old_size/100000}")
            break

with app.app_context():
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


@app.route('/pecha', methods=['POST'])
async def generate():
    form = PechaForm(slide_duration=20, ai_choice="stability")

    title = form['title'].data
    inputs = form['inputs'].data.split("\n")
    slide_duration = form['slide_duration'].data
    ai  = request.form.get('ai_choice', 'stability')

    clean_data()
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
