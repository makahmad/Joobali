from google.appengine.ext import ndb


def get_id_by_kind(key, kind):
    for pair in key.pairs():
        if pair[0] == kind:
            return pair[1]
    return ""

