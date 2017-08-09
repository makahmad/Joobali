from models import Program
from login.models import Provider
from datetime import timedelta
from calendar import monthrange
import logging

logger = logging.getLogger(__name__)


def list_program_by_provider_user_id(user_id):
    """List all programs given a provider id"""
    provider = Provider.get_by_id(user_id)
    programs = Program.query(ancestor=provider.key).order(-Program.startDate, Program.programName)
    return programs

def get_first_bill_due_date(program):
    """ Gets the first bill due date after the program starts. """
    start_date = program.startDate
    if program.billingFrequency == 'Weekly':
        bill_weekday = 0
        if program.weeklyBillDay == 'Monday':
            bill_weekday = 0
        elif program.weeklyBillDay == 'Tuesday':
            bill_weekday = 1
        elif program.weeklyBillDay == 'Wednesday':
            bill_weekday = 2
        elif program.weeklyBillDay == 'Thursday':
            bill_weekday = 3
        elif program.weeklyBillDay == 'Friday':
            bill_weekday = 4
        elif program.weeklyBillDay == 'Saturday':
            bill_weekday = 5
        elif program.weeklyBillDay == 'Sunday':
            bill_weekday = 6
        start_weekday = start_date.weekday()
        if (bill_weekday >= start_weekday):
            return start_date + timedelta(days=bill_weekday - start_weekday)
        else:
            return start_date + timedelta(days=7 + bill_weekday - start_weekday)
    elif program.billingFrequency == 'Monthly':
        if program.monthlyBillDay == 'Last Day':
            return start_date.replace(day=monthrange(start_date.year, start_date.month)[1])
        else:
            bill_day = int(program.monthlyBillDay)
            start_day = start_date.day
            if bill_day > 0 and bill_day <= 28:
                if bill_day >= start_day:
                    return start_date.replace(day=bill_day)
                else:
                    return start_date.replace(day=bill_day) + timedelta(days=monthrange(start_date.year, start_date.month)[1])
    # if everything fall through, just return progrma start date.
    return start_date
