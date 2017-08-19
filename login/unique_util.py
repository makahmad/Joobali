from google.appengine.ext import ndb
from login.models import Unique
from home.models import InitSetupStatus


@ndb.transactional(xg=True)
def upsert_parent(email, parent_key, overwrite=True):
    email = email.lower()
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

@ndb.transactional(xg=True)
def update_provider(old_email, new_email, provider_key):
    old_email = old_email.lower()
    new_email = new_email.lower()
    old_unique = Unique.get_by_id(old_email)
    if old_unique is None:
        raise RuntimeError("Error: not previous Unique object for email (%s) " % (old_email))
    old_unique.key.delete()

    new_unique = Unique.get_by_id(new_email)
    if new_unique is not None:
        raise RuntimeError("Error: Unique object already taken for email (%s) " % (new_email))

    update_init_setup_status(old_email, new_email)

    new_unique = Unique(id=new_email)
    new_unique.email = new_email
    new_unique.provider_key = provider_key
    new_unique.put()

@ndb.transactional(xg=True)
def update_parent(old_email, new_email, parent_key):
    old_email = old_email.lower()
    new_email = new_email.lower()
    old_unique = Unique.get_by_id(old_email)
    if old_unique is None:
        raise RuntimeError("Error: not previous Unique object for email (%s) " % (old_email))
    old_unique.key.delete()

    new_unique = Unique.get_by_id(new_email)
    if new_unique is not None:
        raise RuntimeError("Error: Unique object already taken for email (%s) " % (new_email))

    update_init_setup_status(old_email, new_email)

    new_unique = Unique(id=new_email)
    new_unique.email = new_email
    new_unique.parent_key = parent_key
    new_unique.put()

def update_init_setup_status(old_email, new_email):
    old_email = old_email.lower()
    new_email = new_email.lower()
    setup_done = False
    old_init_setup = InitSetupStatus.get_by_id(old_email)
    if old_init_setup:
        setup_done = old_init_setup.setupFinished
    new_init_setup = InitSetupStatus(id=new_email)
    new_init_setup.email = new_email
    new_init_setup.setupFinished = setup_done
    new_init_setup.put()
