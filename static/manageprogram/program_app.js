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

ProgramController = function($scope, $http) {
	this.http_ = $http;
	this.scope_ = $scope;
    this.scope_.programs = [];
	this.scope_.sessions = [];
	this.scope_.newSession = {};
	this.scope_.newProgram = {"feeType": "Hourly", "billingFrequency": "Monthly"};

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


ProgramController.prototype.addNewSession = function() {
	if (this.validateCurrentForm()) {
		var newSession = {};
		newSession.sessionName = this.scope_.newSession.sessionName;
		// Temp Hack: datetimepicker doesn't work with Angular ng-model, so here we manually copy the value over.
		newSession.startTime = $('#startTime').val();
		newSession.endTime = $('#endTime').val();

		var dates = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
		var selectedDates = [];
		for (i in dates) {

			if (this.scope_.newSession[dates[i]] == true) {
				selectedDates.push(dates[i]);
			}
		}

		newSession.repeatOn = selectedDates.toString();
		console.log(newSession);

		this.scope_.sessions.push(newSession);
	}
};

ProgramController.prototype.validateCurrentForm = function() {
	var curContent = $(".form-content.current");
  	var curNav = $(".form-nav.current");

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
	}
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
			$('#addProgramModal').modal({ show: false})
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
