from google.appengine.ext import ndb
from models import Program
from login.models import Provider
from common import key_util
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def list_program_by_provider_email(provider_email):
    """List all programs given a provider id"""
    provider = Provider.get_by_id(provider_email)
    programs = Program.query(ancestor=provider.key)
    return programs