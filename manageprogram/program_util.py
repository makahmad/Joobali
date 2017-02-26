from models import Program
from login.models import Provider
import logging

logger = logging.getLogger(__name__)


def list_program_by_provider_user_id(user_id):
    """List all programs given a provider id"""
    provider = Provider.get_by_id(user_id)
    programs = Program.query(ancestor=provider.key)
    return programs
