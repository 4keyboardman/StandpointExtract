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


@bp.route('/chatbot/cluster/threshold/<value>', methods=["GET"])
def set_chatbot_threshold(value):
    try:
        current_app.nlp_model.chatbot.cluster_threshold = float(value)
        return 'success'
    except ValueError:
        return 'error'


@bp.route('/chatbot/cluster/threshold', methods=["GET"])
def get_cluster_threshold():
    return str(current_app.nlp_model.chatbot.cluster_threshold)


@bp.route('/chatbot/search/threshold/<value>', methods=["GET"])
def set_search_threshold(value):
    try:
        current_app.nlp_model.chatbot.search_threshold = float(value)
        return 'success'
    except ValueError:
        return 'error'


@bp.route('/chatbot/search/threshold', methods=["GET"])
def get_search_threshold():
    return str(current_app.nlp_model.chatbot.search_threshold)


@bp.route('/chatbot/cluster/nearest/<value>', methods=["GET"])
def set_chatbot_nearest(value):
    try:
        current_app.nlp_model.chatbot.cluster_nearest = float(value)
        return 'success'
    except ValueError:
        return 'error'


@bp.route('/chatbot/cluster/nearest', methods=["GET"])
def get_cluster_nearest():
    return str(current_app.nlp_model.chatbot.cluster_nearest)
