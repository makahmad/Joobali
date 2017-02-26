"""Package for common json encoding class"""
from datetime import datetime, date, time
from google.appengine.ext import ndb
import json


class JEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ndb.Model):
            result = o.to_dict()
            result['id'] = o.key.id()
            return result
        elif isinstance(o, ndb.Key):
            return o.pairs()
        elif isinstance(o, datetime):
            return o.isoformat()	  # Or whatever other date format you're OK with...
        elif isinstance(o, date):
            return o.strftime('%m/%d/%Y')
        elif isinstance(o, time):
            return o.strftime('%I:%M %p')
