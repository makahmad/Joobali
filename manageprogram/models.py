from google.appengine.ext import ndb

class Program(ndb.Model):
	programName = ndb.StringProperty(required=True)
	startDate = ndb.DateProperty(required=True)
	endDate = ndb.DateProperty()
	#maxCapacity = ndb.IntegerProperty()
	registrationFee = ndb.FloatProperty()
	fee = ndb.FloatProperty(required=True)
	#feeType = ndb.StringProperty(required=True) #enum: hourly, tuition
	#lateFee = ndb.FloatProperty()  # default to general setting if blank.
	#dueDate = ndb.DateProperty(required=True) # initial payment due date.
	billingFrequency = ndb.StringProperty(required=True) #enum: weekly, monthly(defualt)

	# Example model static method:
	#  @staticmethod
	# def listProgramsByProvider(provider):
	# 	''' Returns a list of Programs associated with the provider'''
	# 	programs = Program.query(ancestor=provider.key)
	# 	return programs

class Session(ndb.Model):
	sessionName = ndb.StringProperty(required=True)
	startTime = ndb.TimeProperty(required=True) #TODO:change DateTime to Time
	endTime = ndb.TimeProperty(required=True)
	repeatOn = ndb.StringProperty(required=True) #enum: Sun, Mon, Tue, Wed, Thu, Fri, Sat
