var TIME_FORMAT =  'hh:mm A';

EditProgramComponentController = function($scope,$uibModal,$http, $window, $location) {
//    console.log('EditProgramComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.program = {};
	this.sessions = [];
	this.newSession = {};
    this.showConflictLabel = false;
    this.location_ = $location;
    this.dateFormat = "MM/DD/YYYY";


//	this.initializeTimePickers();

    var $ctrl = this;
    this.program.showLastDayCheckbox = false;

//    $ctrl.weeklyBillDays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
//
//    $ctrl.monthlyBillDays = [];
//    for(var i=1;i<=28;i++)
//        $ctrl.monthlyBillDays.push(i);
//     $ctrl.monthlyBillDays.push("Last Day");


    $ctrl.$onInit = function () {

          	$http({
            method: 'GET',
            url: '/manageprogram/getprogram',
            params: {id: $ctrl.resolve.programId}
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available

            this.program = JSON.parse(response.data[0]);
            this.program.hasEnrollment = response.data[1].hasEnrollment;

            var startDate = moment(new Date(this.program.startDate));

            this.dayOfWeekDisplayOnly = startDate.format('dddd'); //change 0 to Sunday, 1 to Monday....
            this.dayOfMonthDisplayOnly = startDate.format('Do'); //change 1 to 1st, 2 to 2nd....
            this.startDateDisplayOnly = startDate.format('MM/DD/YYYY');

            this.openStartDatePicker = false;
            this.endDatePickerOpened = false;

            this.showLastDayCheckbox = false;
            this.disableLastDayCheckbox = false;


            this.whenChangeEndDate();

            this.startDatePickerOptions = {
                minDate: moment().add(6, 'day')
            }

            this.endDatePickerOptions = {
                minDate: startDate.add(1, 'day'),
                dateDisabled: angular.bind(this, this.disabledEndDate)
            }


            $ctrl.openStartDatePicker = function () {
                this.startDatePickerOpened = true;
            };

            $ctrl.openEndDatePicker = function () {
                this.endDatePickerOpened = true;
            };

            this.program.startDate = new Date(this.program.startDate);

            if (!this.program.indefinite)
                this.program.endDate = new Date(this.program.endDate);



        }), function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response);
        });

    };

        $ctrl.cancel = function () {
          $ctrl.dismiss({$value: 'cancel'});
        };

    $ctrl.deleteProgram = function () {
      $ctrl.resolve.confirmDeleteComponentModal();
    };


};


// Disable invalid choices for billing end date
EditProgramComponentController.prototype.disabledEndDate = function(dateAndMode) {

    var result = false;
    var startDate = new Date(this.program.startDate);
    if (dateAndMode.mode === 'day') {

        if (this.program.billingFrequency != null) {

            //if weekly billing then end date must fall on the same day of the week
            if (this.program.billingFrequency === 'Weekly') {
                result =  (dateAndMode.date<=this.program.startDate
                || dateAndMode.date.getDay() != moment(startDate).format('d')
                );
            }

            //if start date is last day of the month, then end date must be last day of the next month
            else if (this.program.billingFrequency === 'Monthly' && this.program.lastDay) {
                var daysInStartDateMonth = moment(startDate).daysInMonth();
                var lastDayInStartDateMonth = moment(startDate).date(daysInStartDateMonth);
                var daysInEndDateMonth = moment(dateAndMode.date).daysInMonth();

                result = (dateAndMode.date<=lastDayInStartDateMonth
                            || dateAndMode.date.getDate() != daysInEndDateMonth);
            }

            //if monthly billing and not last day of the month, then end date must fall on the same day of the month
            else if (this.program.billingFrequency === 'Monthly') {
                result = (dateAndMode.date<=this.program.startDate
                            || dateAndMode.date.getDate() != moment(startDate).format('D'));
            }
        }
    }
    return result;

}

EditProgramComponentController.prototype.whenChangeStartDateOrFrequency = function() {
    var startDate = moment(this.program.startDate);

    this.dayOfWeekDisplayOnly = startDate.format('dddd'); //change 0 to Sunday, 1 to Monday....
    this.dayOfMonthDisplayOnly = startDate.format('Do'); //change 1 to 1st, 2 to 2nd....
    this.startDateDisplayOnly = startDate.format('MM/DD/YYYY');
    this.disableLastDayCheckbox = false;

    //if day of start date is the last day of the month, show Last Day checkbox
    if (startDate.format('D') == startDate.daysInMonth())
    {
       this.program.showLastDayCheckbox = true;

        //if day of last day is the 31st, then check the Last Day checbkox and make it read only
       if (startDate.format('D') == 31)
       {
            this.program.lastDay = true;
            this.disableLastDayCheckbox = true;
       }
    }
    else
    {
        this.program.lastDay = false;
        this.program.showLastDayCheckbox = false;
    }

    this.program.endDate = null;

    this.whenChangeEndDate();
}

EditProgramComponentController.prototype.whenChangeEndDate = function() {

    if(this.program.billingFrequency=='Monthly' && this.program.lastDay)
        this.programInfoDisplay = 'We will automatically collect fees for this program on the last day of '+
        'each month starting '+this.startDateDisplayOnly;
    else if(this.program.billingFrequency=='Monthly' && !this.program.lastDay)
        this.programInfoDisplay = 'We will automatically collect fees for this program on the '+this.dayOfMonthDisplayOnly+
                              ' day of each month starting '+this.startDateDisplayOnly;
    else if(this.program.billingFrequency=='Weekly')
        this.programInfoDisplay = 'We will automatically collect fees for this program weekly on '+this.dayOfWeekDisplayOnly+'s'+
                              ' starting '+this.startDateDisplayOnly;

    if(this.program.endDate)
        this.programInfoDisplay += ' and ending on '+moment(this.program.endDate).format('MM/DD/YYYY')+'.';
    else
        this.programInfoDisplay += ' indefinitely.'
}

EditProgramComponentController.prototype.whenChangeLastDay = function() {

    if (this.program.startDate && this.program.endDate)
    {
        var endDate = moment(this.program.endDate);
        var startDate = moment(this.program.startDate);


        //if last day is checked, and end date is not last day of a month, clear end date
        if (this.program.lastDay && endDate.format('D') != endDate.daysInMonth())
            this.program.endDate = null;

        //if last day is unchecked, and end date is not the same day of a start month, clear end date
        if (!this.program.lastDay && startDate.format('D')!=endDate.format('D'))
            this.program.endDate = null;

    }

    this.whenChangeEndDate();

}


/*
EditProgramComponentController.prototype.setProgramInfoDisplay = function(program) {
//console.log(program);
    var startDate = moment(program.startDate);

    this.dayOfWeekDisplayOnly = startDate.format('dddd'); //change 0 to Sunday, 1 to Monday....
    this.dayOfMonthDisplayOnly = startDate.format('Do'); //change 1 to 1st, 2 to 2nd....
    this.startDateDisplayOnly = startDate.format('MM/DD/YYYY');

    if(program.billingFrequency=='Monthly' && program.lastDay)
        this.programInfoDisplay = 'We will automatically collect fees for this program on the last day of '+
        'each month starting '+this.startDateDisplayOnly;
    else if(program.billingFrequency=='Monthly' && !program.lastDay)
        this.programInfoDisplay = 'We will automatically collect fees for this program on the '+this.dayOfMonthDisplayOnly+
                              ' day of each month starting '+this.startDateDisplayOnly;
    else if(program.billingFrequency=='Weekly')
        this.programInfoDisplay = 'We will automatically collect fees for this program weekly on '+this.dayOfWeekDisplayOnly+'s'+
                              ' starting '+this.startDateDisplayOnly;

    if(program.endDate)
        this.programInfoDisplay += ' and ending on '+moment(program.endDate).format('MM/DD/YYYY')+'.';
    else
        this.programInfoDisplay += ' indefinitely.'
}

EditProgramComponentController.prototype.initializeTimePickers = function() {
    $('#startDate').datetimepicker({
        format: 'MM/DD/YYYY',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        $('#endDate').data('DateTimePicker').minDate(e.date);
        this.program.startDate = $('#startDate').val();
    }));

    $('#endDate').datetimepicker({
        format: 'MM/DD/YYYY',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        this.program.endDate = $('#endDate').val();
    }));
   /* $('#dueDate').datetimepicker({
        format: 'MM/DD/YYYY',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        this.program.dueDate = $('#dueDate').val();
    }));
**/
/*
    $('#startTime').datetimepicker({
        format: 'hh:mm A',
    })
    .on('dp.hide', angular.bind(this, function(e) {
		this.newSession.startTime = $('#startTime').val();

		this.rollUpEndTime();

		this.showConflictLabel = false;
		this.$apply();
    }));
    $('#endTime').datetimepicker({
        format: 'hh:mm A',
    })
    .on('dp.hide', angular.bind(this, function(e) {
		this.newSession.endTime = $('#endTime').val();

		this.rollUpEndTime();

		this.showConflictLabel = false;
		this.$apply();
    }));
    $('[data-toggle="tooltip"]').tooltip();
};


EditProgramComponentController.prototype.rollUpEndTime = function() {
	var startTime = moment(this.newSession.startTime, TIME_FORMAT);
	var endTime = moment(this.newSession.endTime, TIME_FORMAT);

	if (startTime.isAfter(endTime)) {
		// Roll up end time to equal start time.
		$('#endTime').val($('#startTime').val());
		this.newSession.endTime = $('#endTime').val();
	}
};
*/

EditProgramComponentController.prototype.saveProgram = function() {



    this.program.startDate =  moment(this.program.startDate).format('MM/DD/YYYY');

    this.program.indefinite = false;
    this.program.endDateStr = null;
    if (this.program.endDate!=null)
        this.program.endDate =  moment(this.program.endDate).format('MM/DD/YYYY');
    else
    {
        this.program.endDateStr = "Indefinite";
        this.program.indefinite = true;
    }

	this.http_({
		method: 'POST',
		url: '/manageprogram/updateprogram',
		data: JSON.stringify(this.program)
	}).then(
		angular.bind(this, function (response) {
//			console.log('post suceeded');
            this.program.css = 1;
            this.close({$value : this.program});

		}),
		function (response) {
			console.log('post failed');
			alert("Something is wrong with the saving. Please try again later");
		}
	);
};

EditProgramComponentController.prototype.deleteProgram = function() {
	this.http_({
		method: 'POST',
		url: '/manageprogram/deleteprogram',
		data: JSON.stringify({id: this.program.id})
	}).then(
		angular.bind(this, function (response) {
//			console.log('post suceeded');

			//this.window_.location.href = '/home/dashboard';

			this.location_.path('/programs');
			location.reload();

		}),
		function (response) {
			console.log('post failed');
			alert("Something is wrong with the saving. Please try again later");
		}
	);
};
/*
EditProgramComponentController.prototype.addSession = function(session) {
	session['programId'] = this.programId;
	this.http_({
		method: 'POST',
		url: '/manageprogram/addsession',
		data: JSON.stringify(session)
	}).then(
		function (response) {
//			console.log('post suceeded');
			location.reload();
		},
		function (response) {
			console.log('post failed');
			alert("Something is wrong with the saving. Please try again later");
		}
	);
};


EditProgramComponentController.prototype.saveSession = function() {
	this.newSession['programId'] = this.programId;


	var dates = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
	var selectedDates = [];
	for (i in dates) {

		if (this.newSession[dates[i]] == true) {
			selectedDates.push(dates[i]);
		}
	}

	this.newSession['repeatOn'] = selectedDates.toString();
	this.http_({
		method: 'POST',
		url: '/manageprogram/updatesession',
		data: JSON.stringify(this.newSession)
	}).then(
		function (response) {
//			console.log('post suceeded');
			location.reload();
		},
		function (response) {
			console.log('post failed');
			alert("Something is wrong with the saving. Please try again later");
		}
	);
};


EditProgramComponentController.prototype.deleteSession = function() {
	this.newSession['programId'] = this.programId;

	this.http_({
		method: 'POST',
		url: '/manageprogram/deletesession',
		data: JSON.stringify(this.newSession)
	}).then(
		function (response) {
//			console.log('post suceeded');
			location.reload();
		},
		function (response) {
			console.log('post failed');
			alert("Something is wrong with the saving. Please try again later");
		}
	);
};


EditProgramComponentController.prototype.onSessionChange = function() {
	this.showConflictLabel = false;
};


EditProgramComponentController.prototype.editSession = function(session) {
	if (session.inEdit == true) {
		session.inEdit = false;
		return;
	}
	for (i in this.sessions) {
		this.sessions[i].inEdit = false;
	};
	session.inEdit = true;
	this.newSession = {};
	this.newSession.id = session.id;
	this.newSession.sessionName = session.sessionName;
	this.newSession.startTime = session.startTime;
	this.newSession.endTime = session.endTime;

	var dates = session.repeatOn.split(',');
	for (i in dates) {
		var date = dates[i];
		this.newSession[date] = true;
	}
};


EditProgramComponentController.prototype.isSessionEditing = function() {
	for (i in this.sessions) {
		if (this.sessions[i].inEdit == true) {
			return true;
		}
	};
	return false;
};


EditProgramComponentController.prototype.addNewSession = function() {
	if (this.validateCurrentForm('#sessionForm')) {
		var newSession = {};
		newSession.sessionName = this.newSession.sessionName;
		newSession.startTime = this.newSession.startTime;
		newSession.endTime = this.newSession.endTime;

		var dates = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
		var selectedDates = [];
		for (i in dates) {

			if (this.newSession[dates[i]] == true) {
				selectedDates.push(dates[i]);
			}
		}

		newSession.repeatOn = selectedDates.toString();
//		console.log(newSession);

		if (this.validateNewSession(newSession)) {
			this.addSession(newSession);
		} else {
    		this.showConflictLabel = true;
		}
	}
};


/**
 * Makes sure the new session doesn't conflict with existing sessions.
 * NOTE: the {newSession} input must be fully populated.
 * TODO: refactor this method into a common helper class.
 */
 /*
EditProgramComponentController.prototype.validateNewSession = function(newSession) {

	var dates = newSession.repeatOn.split(',');
	var startTime = moment(newSession.startTime, TIME_FORMAT);
	var endTime = moment(newSession.endTime, TIME_FORMAT);

	dateToSessionMap = {};
	for (i in this.sessions) {
		var session = this.sessions[i];
		tempDates = session.repeatOn.split(',');
		for (j in tempDates) {
			var date = tempDates[j];
			if (dateToSessionMap[date]) {
				dateToSessionMap[date].push({'startTime': session.startTime, 'endTime': session.endTime});
			} else {
				dateToSessionMap[date] = [{'startTime': session.startTime, 'endTime': session.endTime}];
			}
		}
	}

	for (i in dates) {
		var date = dates[i];
		if (dateToSessionMap[date]) {
			for (j in dateToSessionMap[date]) {
				var session = dateToSessionMap[date][j];
				var start = moment(session.startTime, TIME_FORMAT);
				var end = moment(session.endTime, TIME_FORMAT);

				if (startTime.isBetween(start, end, null, '[]') || endTime.isBetween(start, end, null, '[]') || start.isBetween(startTime, endTime, null, '[]') || end.isBetween(startTime, endTime, null, '[]')) {
					return false;
				}
			}
		}
	}
	return true;
};
*/

EditProgramComponentController.prototype.validateCurrentForm = function(formSelector) {
	var curContent = $(formSelector);

  	var curInputs = curContent.find("input"),
  	isValid = true;

	$(".form-group").removeClass("has-error");
	for(var i=0; i< curInputs.length; i++){
		if (!curInputs[i].validity.valid){
			isValid = false;
			$(curInputs[i]).closest(".form-group").addClass("has-error");
		}
	}
	if (curContent.find('div.checkbox-group.required :checkbox').length > 0 && curContent.find('div.checkbox-group.required :checkbox:checked').length == 0) {
		isValid = false;
		requiredBoxes = curContent.find('div.checkbox-group.required :checkbox');
		for (var i = 0; i < requiredBoxes.length; i++) {
			$(requiredBoxes[i]).closest(".form-group").addClass("has-error")
		}
	}
	return isValid;
};