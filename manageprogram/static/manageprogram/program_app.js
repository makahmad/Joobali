function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');


var TIME_FORMAT =  'hh:mm A';

ProgramController = function($scope, $http, $window) {
	this.http_ = $http;
	this.window_ = $window;
	this.scope_ = $scope;
    this.scope_.programs = [];
	this.scope_.sessions = [];
	this.scope_.newSession = {};
	this.scope_.newProgram = {"feeType": "Hourly", "billingFrequency": "Monthly"};

    this.scope_.showConflictLabel = false;
    $http({
	  method: 'GET',
	  url: '/manageprogram/listprograms'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    console.log(response);
	    this.scope_.programs = [];
	    angular.forEach(response.data, angular.bind(this, function(program) {
	    	this.scope_.programs.push(JSON.parse(program));
	    }));
	    console.log(this.scope_.programs);

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });

	this.initializeTimePickers();
};

ProgramController.prototype.initializeTimePickers = function() {
    $('#startDate').datetimepicker({
        format: 'YYYY-MM-DD',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        $('#endDate').data('DateTimePicker').minDate(e.date);
        this.scope_.newProgram.startDate = $('#startDate').val();
    }));

    $('#endDate').datetimepicker({
        format: 'YYYY-MM-DD',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        this.scope_.newProgram.endDate = $('#endDate').val();
    }));
    $('#dueDate').datetimepicker({
        format: 'YYYY-MM-DD',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        this.scope_.newProgram.dueDate = $('#dueDate').val();
    }));

    $('#startTime').datetimepicker({
        format: 'hh:mm A',
    })
    .on('dp.hide', angular.bind(this, function(e) {
		this.scope_.newSession.startTime = $('#startTime').val();

		this.rollUpEndTime();

		this.scope_.showConflictLabel = false;
		this.scope_.$apply();
    }));
    $('#endTime').datetimepicker({
        format: 'hh:mm A',
    })
    .on('dp.hide', angular.bind(this, function(e) {
		this.scope_.newSession.endTime = $('#endTime').val();

		this.rollUpEndTime();

		this.scope_.showConflictLabel = false;
		this.scope_.$apply();
    }));
    $('[data-toggle="tooltip"]').tooltip();
};


ProgramController.prototype.rollUpEndTime = function() {
	var startTime = moment(this.scope_.newSession.startTime, TIME_FORMAT);
	var endTime = moment(this.scope_.newSession.endTime, TIME_FORMAT);

	if (startTime.isAfter(endTime)) {
		// Roll up end time to equal start time.
		$('#endTime').val($('#startTime').val());
		this.scope_.newSession.endTime = $('#endTime').val();
	}
};


ProgramController.prototype.onSessionChange = function() {
	this.scope_.showConflictLabel = false;
};


ProgramController.prototype.setNewProgram = function() {
	var newProgram = {};
	newProgram.programName = this.scope_.newProgram.programName;
	newProgram.maxCapacity = this.scope_.newProgram.maxCapacity;
	newProgram.registrationFee = this.scope_.newProgram.registrationFee;
	newProgram.fee = this.scope_.newProgram.fee;
	newProgram.feeType = this.scope_.newProgram.feeType;
	newProgram.lateFee = this.scope_.newProgram.lateFee;
	newProgram.billingFrequency = this.scope_.newProgram.billingFrequency;
	// Temp Hack: datetimepicker doesn't work with Angular ng-model, so here we manually copy the value over.
	newProgram.startDate = $('#startDate').val();
	newProgram.endDate = $('#endDate').val();
	newProgram.dueDate = $('#dueDate').val();

	this.scope_.newProgram = newProgram;
};


ProgramController.prototype.editProgram = function(id) {
	console.log(id);
	this.window_.location.href = '/manageprogram/edit?id=' + id;
};


ProgramController.prototype.addNewSession = function() {
	if (this.validateCurrentForm()) {
		var newSession = {};
		newSession.sessionName = this.scope_.newSession.sessionName;
		newSession.startTime = this.scope_.newSession.startTime;
		newSession.endTime = this.scope_.newSession.endTime;

		var dates = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
		var selectedDates = [];
		for (i in dates) {

			if (this.scope_.newSession[dates[i]] == true) {
				selectedDates.push(dates[i]);
			}
		}

		newSession.repeatOn = selectedDates.toString();
		console.log(newSession);

		if (this.validateNewSession(newSession)) {
			this.scope_.sessions.push(newSession);
		} else {
    		this.scope_.showConflictLabel = true;
		}
	}
};


/**
 * Makes sure the new session doesn't conflict with existing sessions.
 * NOTE: the {newSession} input must be fully populated.
 */
ProgramController.prototype.validateNewSession = function(newSession) {

	var dates = newSession.repeatOn.split(',');
	var startTime = moment(newSession.startTime, TIME_FORMAT);
	var endTime = moment(newSession.endTime, TIME_FORMAT);

	dateToSessionMap = {};
	for (i in this.scope_.sessions) {
		var session = this.scope_.sessions[i];
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


ProgramController.prototype.validateCurrentForm = function() {
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
	console.log(curContent.find('div.checkbox-group.required :checkbox'));
	if (curContent.find('div.checkbox-group.required :checkbox').length > 0 && curContent.find('div.checkbox-group.required :checkbox:checked').length == 0) {
		isValid = false;
		requiredBoxes = curContent.find('div.checkbox-group.required :checkbox');
		for (var i = 0; i < requiredBoxes.length; i++) {
			$(requiredBoxes[i]).closest(".form-group").addClass("has-error")
		}
	}
	return isValid;
};


ProgramController.prototype.handleNext = function() {
	var curContent = $(".form-content.current");
	var curNav = $(".form-nav.current");
  if (curNav.attr('id') === "navStep2" || this.validateCurrentForm()) {
	  curNav.removeClass("current");
	  curNav.next().addClass("current");
	  curNav.next().addClass("active");

	  curContent.removeClass("current");
	  curContent.next().addClass("current");

	  if (curNav.next().attr('id') === "navStep3") {
		  $("#nextButton").hide();
		  $("#saveButton").show();
	  } else {
		  $("#nextButton").show();
		  $("#saveButton").hide();
	  }
	  if (curNav.attr('id') === 'navStep1') {
		  this.setNewProgram();
	  }
  }
};


ProgramController.prototype.handleSave = function() {
	var data = {
		'program': this.scope_.newProgram,
		'sessions': this.scope_.sessions
	};
	this.http_({
		method: 'POST',
		url: '/manageprogram/addprogram',
		headers: {
			'X-CSRFToken': csrftoken
		},
		data: JSON.stringify(data)
	}).then(
		function (response) {
			console.log('post suceeded');
			location.reload();
		},
		function (response) {
			console.log('post failed');
			alert("Something is wrong with the saving. Please try again later");
		}
	);
};


ProgramController.prototype.setCurrent = function(event) {
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

app = angular.module('programApp', []);
app.controller('ProgramCtrl', ProgramController);
