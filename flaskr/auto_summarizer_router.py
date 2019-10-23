from flaskr import auto_summarizer

from flask import Blueprint
from flask import render_template
from flask import request, session

bp = Blueprint("auto_summarizer", __name__)


@bp.route('/auto_summarizer', methods=["GET"])
def index():
    ratio = request.args.get("ratio")
    if ratio:
        session['extractor'] = ratio
    rank = request.args.get("rank")
    if rank:
        session['auto_summarizer.rank'] = rank
    alpha = request.args.get("alpha")
    if alpha:
        session['auto_summarizer.alpha'] = alpha
    return render_template("auto_summarizer.html")


@bp.route('/auto_summarizer', methods=["POST"])
def auto_summarize():
    text = request.form['text']
    ratio = 0.2
    alpha = 1.0
    rank = 'sentence_rank'
    if 'auto_summarizer.ratio' in session and session['auto_summarizer.ratio']:
        ratio = session['auto_summarizer.ratio']
    if 'auto_summarizer.rank' in session and session['auto_summarizer.rank']:
        rank = session['auto_summarizer.rank']
    if 'auto_summarizer.alpha' in session and session['auto_summarizer.alpha']:
        alpha = session['auto_summarizer.alpha']
    return auto_summarizer.summarize(text, ratio=float(ratio), rank=rank, alpha=float(alpha))
