import json

from flask import Blueprint
from flask import render_template
from flask import request

from flaskr import chatbot

bp = Blueprint("chatbot", __name__)


@bp.route('/chatbot', methods=["GET"])
def index():
    return render_template("chatbot.html")


@bp.route('/chatbot', methods=["POST"])
def receive():
    message = request.form['message']
    res = chatbot.handle(message.strip())
    reply = [{"answer": i} for i in res]
    return json.dumps(reply)
