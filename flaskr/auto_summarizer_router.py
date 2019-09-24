from flaskr import auto_summarizer

from flask import Blueprint
from flask import render_template
from flask import request
from flask import current_app

bp = Blueprint("auto_summarizer", __name__)


@bp.route('/auto_summarizer', methods=["GET"])
def index():
    return render_template("auto_summarizer.html")


@bp.route('/auto_summarizer', methods=["POST"])
def auto_summarize():
    text = request.form['text']
    return auto_summarizer.summarize(text, rank=current_app.nlp_model.auto_summarizer['rank'])
