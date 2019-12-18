from flaskr import nlp_model
from flaskr.extractor import SpeckExtractor
from flask import Blueprint
from flask import current_app

bp = Blueprint("cmd", __name__, url_prefix="/cmd")


@bp.route('/model/reload', methods=["GET"])
def reload():
    nlp_model.init_model(current_app)
    return 'success'


@bp.route('/extractor/<any(rnn, sif, mix):model>', methods=["GET"])
def set_extractor(model):
    return 'success' if current_app.nlp_model.set_extractor(model) else 'error: invalid model.'


@bp.route('/extractor', methods=["GET"])
def get_extractor():
    extractor = current_app.nlp_model.extractor
    return 'rnn' if type(extractor) == SpeckExtractor else 'sif'


@bp.route('/chatbot/threshold/<value>', methods=["GET"])
def set_chatbot_threshold(value):
    try:
        current_app.nlp_model.chatbot.threshold = float(value)
        return 'success'
    except ValueError:
        return 'error'


@bp.route('/chatbot/threshold', methods=["GET"])
def get_chatbot_threshold():
    return str(current_app.nlp_model.chatbot.threshold)
