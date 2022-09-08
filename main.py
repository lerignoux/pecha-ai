import logging

from flask import Flask, render_template


log = logging.getLogger('peka-ai')

parser = argparse.ArgumentParser(description='Show transversal xml properties.')
parser.add_argument('--debug', '-d', dest='debug',
                    action='store_true',
                    help='Debug mode')


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
    return render_template('root.html')


if __name__ == "__main__":
    args = parser.parse_args()
    app.run(host='0.0.0.0', port='8080', debug=args.debug)
