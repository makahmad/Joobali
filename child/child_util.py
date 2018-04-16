# External Libraries
from google.appengine.ext import ndb
import logging
# Internal Libraries
from models import Child
from models import ProviderChildView
from enrollment import enrollment_util
from datetime import datetime

logger = logging.getLogger(__name__)


def add_child(to_be_added_child, parent_key):
    """Input should be a dict containing all the Child Model's data"""
    child = to_be_added_child
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


# TODO(zilong): Make this transactional
def get_existing_child(child, parent_key):
    children = list_child_by_parent(parent_key=parent_key)
    for existing_child in children:
        if not existing_child.is_deleted and match_child(child, existing_child):
            return existing_child
    return None


def list_child_by_provider(provider_key):
    provider_children_views = get_provider_child_view(provider_key=provider_key)
    children = list()

    for view in provider_children_views:
        child = view.child_key.get().to_dict()
        if not child['is_deleted']:
            child['id'] = view.child_key.get().key.id()
            child['parent_name'] = None
            child['parent_status'] = view.child_key.get().parent_key.get().status.status
            if view.child_key.get().parent_key.get().first_name or view.child_key.get().parent_key.get().last_name:
                child['parent_name'] = view.child_key.get().parent_key.get().first_name + ' ' + view.child_key.get().parent_key.get().last_name
                child['parent_phone'] = view.child_key.get().parent_key.get().phone
            children.append(child)

    #todo hardcoded to UTF8
    children = sorted(children, key = lambda d: (d['first_name'].encode('UTF8').lower()))

    return children


def list_child_by_provider_program(provider_id, program_id):
    provider_id = int(provider_id)
    program_id = int(program_id)
    logger.info("listing child by provider %d and program %d" % (provider_id, program_id))
    enrollments = enrollment_util.list_enrollment_by_provider_program(provider_id=provider_id, program_id=program_id)
    children = list()
    for enrollment in enrollments:
        child = enrollment.child_key.get().to_dict()
        if not child['is_deleted']:
            child['id'] = enrollment.child_key.get().key.id()
            child['parent_name'] = None
            if enrollment.child_key.get().parent_key.get().first_name or enrollment.child_key.get().parent_key.get().last_name:
                child['parent_name'] = enrollment.child_key.get().parent_key.get().first_name + ' ' + enrollment.child_key.get().parent_key.get().last_name
                child['parent_phone'] = enrollment.child_key.get().parent_key.get().phone
            children.append(child)

    #todo hardcoded to UTF8
    children = sorted(children, key = lambda d: (d['first_name'].encode('UTF8').lower()))

    return children


# TODO(zilong): Implement this for parent page
def list_child_by_parent(parent_key):
    query = Child.query(Child.parent_key == parent_key)
    children = list()
    for child in query:
        if child.is_deleted is not None and child.is_deleted == False:
            children.append(child)
    return children


def update_child(child_key, child_data):
    """
        Update child with new child_data
    """
    child = child_key.get()
    if 'date_of_birth' in child_data:
        child.date_of_birth = datetime.strptime(child_data['date_of_birth'], "%m/%d/%Y").date()

    if 'first_name' in child_data:
        child.first_name = child_data['first_name']

    if 'last_name' in child_data:
        child.last_name = child_data['last_name']

    return child.put()


def match_child(child1, child2):
    if child1.first_name == child2.first_name:
        if child1.last_name == child2.last_name:
            if child1.date_of_birth == child2.date_of_birth:
                if child1.parent_email == child2.parent_email:
                    return True
    return False

