from flask import current_app
import random


def handle(message):
    cluster = current_app.nlp_model.cluster
    res = cluster(message, random.randint(1, 3))
    d = {}
    reply = []
    for i in res:
        if i[1] not in d:
            reply.append(i)
            d[i[1]] = True
    return reply
