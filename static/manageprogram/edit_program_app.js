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

EditProgramController = function($scope, $http, $window, $location) {
	this.http_ = $http;
	this.window_ = $window;
	this.location_ = $location;
	this.scope_ = $scope;
	this.scope_.program = {};
	this.scope_.sessions = [];
	this.scope_.newSession = {};
    this.scope_.showConflictLabel = false;

	$http({
		method: 'GET',
		url: '/manageprogram/getprogram',
		headers: {
			'X-CSRFToken': csrftoken
		},
		params: {id: this.location_.search().id}
	}).then(angular.bind(this, function successCallback(response) {
		// this callback will be called asynchronously
		// when the response is available

		this.scope_.program = JSON.parse(response.data[0]);

	}), function errorCallback(response) {
		// called asynchronously if an error occurs
		// or server returns response with an error status.
		console.log(response);
	});

	$http({
		method: 'GET',
		url: '/manageprogram/listsessions',
		headers: {
			'X-CSRFToken': csrftoken
		},
		params: {id: this.location_.search().id}
	}).then(angular.bind(this, function successCallback(response) {
		// this callback will be called asynchronously
		// when the response is available
		console.log(response);
	    this.scope_.sessions = [];
	    angular.forEach(response.data, angular.bind(this, function(session) {
	    	this.scope_.sessions.push(JSON.parse(session));
	    }));
		console.log(this.scope_.sessions);

	}), function errorCallback(response) {
		// called asynchronously if an error occurs
		// or server returns response with an error status.
		console.log(response);
	});
	this.initializeTimePickers();
};


EditProgramController.prototype.initializeTimePickers = function() {
    $('#startDate').datetimepicker({
        format: 'YYYY-MM-DD',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        $('#endDate').data('DateTimePicker').minDate(e.date);
        this.scope_.program.startDate = $('#startDate').val();
    }));

    $('#endDate').datetimepicker({
        format: 'YYYY-MM-DD',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        this.scope_.program.endDate = $('#endDate').val();
    }));
    $('#dueDate').datetimepicker({
        format: 'YYYY-MM-DD',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        this.scope_.program.dueDate = $('#dueDate').val();
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


EditProgramController.prototype.rollUpEndTime = function() {
	var startTime = moment(this.scope_.newSession.startTime, TIME_FORMAT);
	var endTime = moment(this.scope_.newSession.endTime, TIME_FORMAT);

	if (startTime.isAfter(endTime)) {
		// Roll up end time to equal start time.
		$('#endTime').val($('#startTime').val());
		this.scope_.newSession.endTime = $('#endTime').val();
	}
};


EditProgramController.prototype.saveProgram = function() {
	this.http_({
		method: 'POST',
		url: '/manageprogram/updateprogram',
		headers: {
			'X-CSRFToken': csrftoken
		},
		data: JSON.stringify(this.scope_.program)
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


EditProgramController.prototype.addSession = function(session) {
	session['programId'] = this.location_.search().id;
	this.http_({
		method: 'POST',
		url: '/manageprogram/addsession',
		headers: {
			'X-CSRFToken': csrftoken
		},
		data: JSON.stringify(session)
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


EditProgramController.prototype.saveSession = function() {
	this.scope_.newSession['programId'] = this.location_.search().id;


	var dates = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
	var selectedDates = [];
	for (i in dates) {

		if (this.scope_.newSession[dates[i]] == true) {
			selectedDates.push(dates[i]);
		}
	}

	this.scope_.newSession['repeatOn'] = selectedDates.toString();
	this.http_({
		method: 'POST',
		url: '/manageprogram/updatesession',
		headers: {
			'X-CSRFToken': csrftoken
		},
		data: JSON.stringify(this.scope_.newSession)
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


EditProgramController.prototype.deleteSession = function() {
	this.scope_.newSession['programId'] = this.location_.search().id;

	this.http_({
		method: 'POST',
		url: '/manageprogram/deletesession',
		headers: {
			'X-CSRFToken': csrftoken
		},
		data: JSON.stringify(this.scope_.newSession)
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


EditProgramController.prototype.onSessionChange = function() {
	this.scope_.showConflictLabel = false;
};


EditProgramController.prototype.deleteProgram = function() {
	this.http_({
		method: 'POST',
		url: '/manageprogram/deleteprogram',
		headers: {
			'X-CSRFToken': csrftoken
		},
		data: JSON.stringify({id: this.location_.search().id})
	}).then(
		angular.bind(this, function (response) {
			console.log('post suceeded');

			this.window_.location.href = '/manageprogram';
		}),
		function (response) {
			console.log('post failed');
			alert("Something is wrong with the saving. Please try again later");
		}
	);
};


EditProgramController.prototype.editSession = function(session) {
	if (session.inEdit == true) {
		session.inEdit = false;
		return;
	}
	for (i in this.scope_.sessions) {
		this.scope_.sessions[i].inEdit = false;
	};
	session.inEdit = true;
	this.scope_.newSession = {};
	this.scope_.newSession.id = session.id;
	this.scope_.newSession.sessionName = session.sessionName;
	this.scope_.newSession.startTime = session.startTime;
	this.scope_.newSession.endTime = session.endTime;

	var dates = session.repeatOn.split(',');
	for (i in dates) {
		var date = dates[i];
		this.scope_.newSession[date] = true;
	}
};


EditProgramController.prototype.isSessionEditing = function() {
	for (i in this.scope_.sessions) {
		if (this.scope_.sessions[i].inEdit == true) {
			return true;
		}
	};
	return false;
};

/**
 * TODO: refactor this method into a common helper class.
 */
EditProgramController.prototype.addNewSession = function() {
	if (this.validateCurrentForm('#sessionForm')) {
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
			this.addSession(newSession);
		} else {
    		this.scope_.showConflictLabel = true;
		}
	}
};


/**
 * Makes sure the new session doesn't conflict with existing sessions.
 * NOTE: the {newSession} input must be fully populated.
 * TODO: refactor this method into a common helper class.
 */
EditProgramController.prototype.validateNewSession = function(newSession) {

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


EditProgramController.prototype.validateCurrentForm = function(formSelector) {
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

app = angular.module('editProgramApp', []);
app.config(function($locationProvider) {
        $locationProvider.html5Mode(true);
    });
app.controller('EditProgramCtrl', EditProgramController);
