from google.appengine.ext import ndb
from login.models import Provider


class Program(ndb.Model):
    programName = ndb.StringProperty(required=True)
    startDate = ndb.DateProperty(required=True)
    endDate = ndb.DateProperty()
    registrationFee = ndb.FloatProperty()
    fee = ndb.FloatProperty(required=True)
    lateFee = ndb.FloatProperty()  # default to general setting if blank.
    # dueDate = ndb.DateProperty(required=True) # initial payment due date.
    billingFrequency = ndb.StringProperty(required=True)  #enum: Weekly, Monthly (defualt)

    @classmethod
    def generate_key(cls, provider_id, program_id):
        return ndb.Key(Provider.__name__, provider_id, cls.__name__, program_id)

    # Example model static method:
    #  @staticmethod
    # def listProgramsByProvider(provider):
    # 	''' Returns a list of Programs associated with the provider'''
    # 	programs = Program.query(ancestor=provider.key)
    # 	return programs

# Deprecated
# class Session(ndb.Model):
# 	sessionName = ndb.StringProperty(required=True)
# 	startTime = ndb.TimeProperty(required=True) #TODO:change DateTime to Time
# 	endTime = ndb.TimeProperty(required=True)
# 	repeatOn = ndb.StringProperty(required=True) #enum: Sun, Mon, Tue, Wed, Thu, Fri, Sat
