var TIME_FORMAT =  'hh:mm A';


AddProgramComponentController = function($scope, $http, $window, $filter) {
//    console.log('AddProgramComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.scope_ = $scope;
	this.filter_ = $filter
    this.scope_.programs = [];
	this.scope_.sessions = [];
	this.scope_.newSession = {};
	this.startDate = moment().add(6, 'day');

	this.newProgram = { "startDate": this.startDate,
	                    "endDate": moment().add(7, 'day'),
	                    "billingFrequency": "Monthly",
	                    "weeklyBillDay": "Monday",
	                    "monthlyBillDay": 1,
	                    "indefinite": false,
	                    "lastDay": false};

    if ( this.startDate.format('D') > 28 )
        this.newProgram.lastDay = true;

    this.scope_.showConflictLabel = false;

//	this.initializeTimePickers();
};

AddProgramComponentController.prototype.initializeTimePickers = function() {

    this.newProgram.startDate = moment().add(6, 'day').toDate();

    this.dayOfWeekDisplayOnly = moment(this.newProgram.startDate).format('dddd'); //change 0 to Sunday, 1 to Monday....
    this.dayOfMonthDisplayOnly = moment(this.newProgram.startDate).format('Do'); //change 1 to 1st, 2 to 2nd....
    this.startDateDisplayOnly = moment(this.newProgram.startDate).format('MM/DD/YYYY');

};


AddProgramComponentController.prototype.rollUpEndTime = function() {
	var startTime = moment(this.scope_.newSession.startTime, TIME_FORMAT);
	var endTime = moment(this.scope_.newSession.endTime, TIME_FORMAT);

	if (startTime.isAfter(endTime)) {
		// Roll up end time to equal start time.
		$('#endTime').val($('#startTime').val());
		this.scope_.newSession.endTime = $('#endTime').val();
	}
};


AddProgramComponentController.prototype.onSessionChange = function() {
	this.scope_.showConflictLabel = false;
};



AddProgramComponentController.prototype.validateCurrentForm = function() {
	var curContent = $(".form-content.current");

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


AddProgramComponentController.prototype.handleNext = function() {
	var curContent = $(".form-content.current");
	var curNav = $(".form-nav.current");
  if (curNav.attr('id') === "navStep2" || this.validateCurrentForm()) {
	  curNav.removeClass("current");
	  curNav.next().addClass("current");
	  curNav.next().addClass("active");

	  curContent.removeClass("current");
	  curContent.next().addClass("current");

	 // if (curNav.next().attr('id') === "navStep3") {
		  $("#nextButton").hide();
		  $("#saveButton").show();
	 /* } else {
		  $("#nextButton").show();
		  $("#saveButton").hide();
	  }*/
  }
};


AddProgramComponentController.prototype.handleSave = function() {
    if (this.validateCurrentForm()) {

        this.newProgram.startDate =  moment(this.newProgram.startDate).format('MM/DD/YYYY');

        if (this.newProgram.endDate!=null)
            this.newProgram.endDate =  moment(this.newProgram.endDate).format('MM/DD/YYYY');

        var data = {
            'program': this.newProgram
        };
        this.http_({
            method: 'POST',
            url: '/manageprogram/addprogram',
            data: JSON.stringify(data)
        }).then(
            function (response) {
//                console.log('post suceeded');
                location.reload();
            },
            function (response) {
                console.log('post failed');
                bootbox.alert("Something is wrong with the saving. Please try again later");
            }
        );
    }
};


AddProgramComponentController.prototype.setCurrent = function(event) {
	// User can only move to the visited tabs.
	if ($(event.target).parent().hasClass('active')) {

		$('.nav-pills.nav-wizard > li').removeClass('current');
		$(event.target).parent().addClass('current');
		var contentId = $(event.target).parent().attr('id');

		$('.form-content').removeClass('current');
		$('.' + contentId).addClass('current')
	}

	  if (contentId === "navStep3") {
		  $("#nextButton").hide();
		  $("#saveButton").show();
	  } else {
		  $("#nextButton").show();
		  $("#saveButton").hide();
	  }
};

//
//AddProgramComponentController.prototype.initializeTimePickers = function() {
//    $('#startTime').datetimepicker({
//        format: 'hh:mm A',
//    })
//    .on('dp.hide', angular.bind(this, function(e) {
//		this.scope_.newSession.startTime = $('#startTime').val();
//
//		this.rollUpEndTime();
//
//		this.scope_.showConflictLabel = false;
//		this.scope_.$apply();
//    }));
//    $('#endTime').datetimepicker({
//        format: 'hh:mm A',
//    })
//    .on('dp.hide', angular.bind(this, function(e) {
//		this.scope_.newSession.endTime = $('#endTime').val();
//
//		this.rollUpEndTime();
//
//		this.scope_.showConflictLabel = false;
//		this.scope_.$apply();
//    }));
//    $('[data-toggle="tooltip"]').tooltip();
//};
//
//
//AddProgramComponentController.prototype.rollUpEndTime = function() {
//	var startTime = moment(this.scope_.newSession.startTime, TIME_FORMAT);
//	var endTime = moment(this.scope_.newSession.endTime, TIME_FORMAT);
//
//	if (startTime.isAfter(endTime)) {
//		// Roll up end time to equal start time.
//		$('#endTime').val($('#startTime').val());
//		this.scope_.newSession.endTime = $('#endTime').val();
//	}
//};
//
//
//AddProgramComponentController.prototype.onSessionChange = function() {
//	this.scope_.showConflictLabel = false;
//};
//
//
//AddProgramComponentController.prototype.addNewSession = function() {
//	if (this.validateCurrentForm()) {
//		var newSession = {};
//		newSession.sessionName = this.scope_.newSession.sessionName;
//		newSession.startTime = this.scope_.newSession.startTime;
//		newSession.endTime = this.scope_.newSession.endTime;
//
//		var dates = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
//		var selectedDates = [];
//		for (i in dates) {
//
//			if (this.scope_.newSession[dates[i]] == true) {
//				selectedDates.push(dates[i]);
//			}
//		}
//
//		newSession.repeatOn = selectedDates.toString();
//		console.log(newSession);
//
//		if (this.validateNewSession(newSession)) {
//			this.scope_.sessions.push(newSession);
//		} else {
//    		this.scope_.showConflictLabel = true;
//		}
//	}
//};



/**
 * Makes sure the new session doesn't conflict with existing sessions.
 * NOTE: the {newSession} input must be fully populated.
 */
//AddProgramComponentController.prototype.validateNewSession = function(newSession) {
//
//	var dates = newSession.repeatOn.split(',');
//	var startTime = moment(newSession.startTime, TIME_FORMAT);
//	var endTime = moment(newSession.endTime, TIME_FORMAT);
//
//	dateToSessionMap = {};
//	for (i in this.scope_.sessions) {
//		var session = this.scope_.sessions[i];
//		tempDates = session.repeatOn.split(',');
//		for (j in tempDates) {
//			var date = tempDates[j];
//			if (dateToSessionMap[date]) {
//				dateToSessionMap[date].push({'startTime': session.startTime, 'endTime': session.endTime});
//			} else {
//				dateToSessionMap[date] = [{'startTime': session.startTime, 'endTime': session.endTime}];
//			}
//		}
//	}
//
//	for (i in dates) {
//		var date = dates[i];
//		if (dateToSessionMap[date]) {
//			for (j in dateToSessionMap[date]) {
//				var session = dateToSessionMap[date][j];
//				var start = moment(session.startTime, TIME_FORMAT);
//				var end = moment(session.endTime, TIME_FORMAT);
//
//				if (startTime.isBetween(start, end, null, '[]') || endTime.isBetween(start, end, null, '[]') || start.isBetween(startTime, endTime, null, '[]') || end.isBetween(startTime, endTime, null, '[]')) {
//					return false;
//				}
//			}
//		}
//	}
//	return true;
//};