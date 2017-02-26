from google.appengine.ext import ndb
from login.models import Unique


@ndb.transactional(xg=True)
def upsert_parent(email, parent_key, overwrite=True):
    unique = Unique.get_by_id(email)
    if unique is not None:
        if not overwrite:
            if unique.parent_key != parent_key:
                raise RuntimeError("not overwriting unique %s wit parent_key %s" % (unique, parent_key))
    elif unique is None:
        unique = Unique(id=email)
        unique.email = email
    unique.parent_key = parent_key
    unique.put()

