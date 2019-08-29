from flaskr import nlp_model
from flask import Blueprint
from flask import current_app

bp = Blueprint("cmd", __name__, url_prefix="/cmd")


@bp.route('/model/reload', methods=["GET"])
def reload():
    nlp_model.init_model(current_app)
    return 'success'


@bp.route('/model/<any(rnn, sif):model>', methods=["GET"])
def set_model(model):
    return 'success' if current_app.nlp_model.set_model(model) else 'error: invalid model'
