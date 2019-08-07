from flask import Blueprint
from flask import render_template
from flask import request
from flaskr import extractor

bp = Blueprint("extractor", __name__)


@bp.route('/')
def index():
    return render_template("index.html")


@bp.route('/extract', methods=["POST"])
def extract():
    text = request.form['text']
    return render_template("extract_table.html", table=extractor.extract(text))
