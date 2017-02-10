# External Libraries
from datetime import datetime
from google.appengine.ext import ndb
import logging
# Internal Libraries
from models import Child
from models import ProviderChildView
from parent import parent_util

logger = logging.getLogger(__name__)


def add_child(child_input, parent_key):
    """Input should be a dict containing all the Child Model's data"""
    child = Child()
    child.first_name = child_input['first_name']
    child.last_name = child_input['last_name']
    child.date_of_birth = datetime.strptime(child_input['date_of_birth'], "%m/%d/%Y").date()
    child.parent_email = child_input['parent_email']
    child.parent_key = parent_key
    child.put()
    return child


def add_provider_child_view(child_key, provider_key):
    provider_child_view = ProviderChildView()
    provider_child_view.provider_key = provider_key
    provider_child_view.child_key = child_key
    provider_child_view.put()


def get_provider_child_view(child_key=None, provider_key=None):
    if child_key is None and provider_key is None:
        return None
    results = []
    if child_key is None:
        # Query by provider_key only
        query = ProviderChildView.query(ProviderChildView.provider_key == provider_key)
    elif provider_key is not None:
        # Query by child_key only
        query = ProviderChildView.query(ProviderChildView.child_key == child_key)
    else:
        query = ProviderChildView.query(ProviderChildView.child_key == child_key,
                                        ProviderChildView.provider_key == provider_key)
    if query is not None:
        for provider_child_view in query.fetch():
            results.append(provider_child_view)
    return results


# Check if a child can be viewed by a provider
def check_child_provider_view(child_key, provider_key):
    if child_key is None or provider_key is None:
        raise ValueError("child_key is %s and provider_key is %s" % (child_key, provider_key))
    else:
        query = ProviderChildView.query(ProviderChildView.child_key == child_key,
                                        ProviderChildView.provider_key == provider_key)
        logger.info("query.count() %s" % query.count())
        return query.count() > 0


def get_child_key(child_id):
    return ndb.Key('Child', child_id)


# TODO(zilong): Implement this
def get_existing_child(child_input, parent_id):
    return None


def list_child(provider_key):
    provider_children_views = get_provider_child_view(provider_key=provider_key)
    children = list()
    for view in provider_children_views:
        children.append(view.child_key.get())
    return children


def update_child(child_input, parent_id, child_id):
    child = None
    return child
