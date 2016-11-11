from django.http import HttpResponse
from common.json_encoder import JEncoder
from child.models import Child
from child import child_util
from parent import parent_util

import json
import logging

# Create your views here.

logger = logging.getLogger(__name__)


def list_child(request):
    dummy_child = {"first_name" : "Peter", "last_name" : "Park"}
    return HttpResponse(json.dumps([JEncoder().encode(dummy_child)]), content_type="application/json")


def add_child(request):
    logger.info("request is %s", request)
    parent_email = ""
    parent_input = parent_email
    parent_entity = parent_util.add_parent(parent_input)
    child_input = None
    child_util.add_child(child_input, parent_entity.key)
    pass


def update_child(request):
    pass

