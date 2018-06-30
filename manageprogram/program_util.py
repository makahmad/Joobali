from google.appengine.ext import ndb
from models import Program
from login.models import Provider
from datetime import datetime,timedelta

from calendar import monthrange,day_name
from common import datetime_util

import logging
DATE_FORMAT = '%m/%d/%Y'
logger = logging.getLogger(__name__)

def add_program(provider, newProgram):
    program = Program(parent=provider.key)
    if newProgram['programName']:
        program.programName = newProgram['programName']
    else:
        program.programName = "Program Fee"

    program.registrationFee = newProgram['registrationFee']
    program.fee = newProgram['fee']
    program.lateFee = newProgram['lateFee']
    program.billingFrequency = newProgram['billingFrequency']
    program.startDate = datetime_util.local_to_utc(datetime.strptime(newProgram['startDate'], DATE_FORMAT))
    program.adhoc = newProgram['adhoc']

    if program.billingFrequency == 'Monthly':
        #if program is monthly and last day of month is checked
        if newProgram['lastDay']:
            program.monthlyBillDay = "Last Day"
        else:
            program.monthlyBillDay = str(program.startDate.day)
    else:
        program.weeklyBillDay = day_name[program.startDate.weekday()]

    if newProgram['endDate']:
        program.endDate = datetime_util.local_to_utc(datetime.strptime(newProgram['endDate'], DATE_FORMAT))
    else:
        program.indefinite = True
        program.endDate = None

    program.put()
    return program

def list_program_by_provider_user_id(user_id, program_filter):
    """List all programs given a provider id"""
    provider = Provider.get_by_id(user_id)

    if program_filter is None or program_filter == 'All Programs':
        programs = Program.query(ancestor=provider.key).filter(Program.adhoc == False).order(-Program.startDate, Program.programName)
    # elif program_filter == 'Future':
    #     programs = Program.query(ancestor=provider.key).filter(Program.startDate > datetime.today()).order(-Program.startDate, Program.programName)
    elif program_filter == 'Past':
        programs = Program.query(ancestor=provider.key).filter(Program.endDate < datetime.today(), Program.endDate != None, Program.adhoc == False).order(Program.endDate, Program.programName)
    elif program_filter == 'Current/Upcoming':
        programs = Program.query(ancestor=provider.key).filter(ndb.OR(Program.endDate >= datetime.today(), Program.endDate == None),Program.adhoc ==  False ).order(
            -Program.endDate, Program.programName)

        #Since datastore doesn't allow multiple inequalities, I have to manually filter the endDate as startDate
        #was already a filter in the 'Current' query
        # current_programs = list()
        # for program in programs:
        #     # print(program.startDate)
        #     if program.endDate is None or program.startDate >= datetime.today():
        #         current_programs.append(program)
        # programs = current_programs

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
                    return start_date.replace(day=bill_day) + timedelta(
                        days=monthrange(start_date.year, start_date.month)[1])
    # if everything fall through, just return progrma start date.
    return start_date
