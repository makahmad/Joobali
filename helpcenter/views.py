import json
import logging

from django.http import HttpResponse, HttpResponseServerError
from django.http import HttpResponseRedirect
from time import strftime, strptime
from datetime import datetime, date, time
from common.json_encoder import JEncoder
from common.session import check_session
from login.models import Provider
from helpcenter.models import Help
from passlib.apps import custom_app_context as pwd_context

DATE_FORMAT = '%m/%d/%Y'
logger = logging.getLogger(__name__)


def sendComments(request):
    """Stores question or comment"""
    if not check_session(request):
        return HttpResponseRedirect('/login')

    if not request.session['is_provider']:
        return HttpResponseRedirect('/login')

    help = json.loads(request.body)

    # provider
    provider = Provider.get_by_id(request.session['user_id'])

    newCommentQuestion = Help()
    newCommentQuestion.comments = help['comments']
    newCommentQuestion.email = provider.email
    newCommentQuestion.name = provider.firstName+' '+provider.lastName
    newCommentQuestion.phone = provider.phone
    newCommentQuestion.date_created = datetime.now()
    newCommentQuestion.put()

    return HttpResponse('success')