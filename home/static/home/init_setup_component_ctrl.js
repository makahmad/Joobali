InitSetupComponentController = function($http) {
    console.log('InitSetupComponentController running');
    this.dateOfBirthPickerOpened = false;
    this.isDone = false;
    self = this
    this.openDateOfBirthPicker = function() {
        console.log("Toggle Date picker: " + this.dateOfBirthPickerOpened);
        this.dateOfBirthPickerOpened = ! this.dateOfBirthPickerOpened;
    };

    this.http_ = $http;
	this.newProgram = {"feeType": "Hourly", "billingFrequency": "Monthly"};
	$http({
	  method: 'GET',
	  url: '/login/isinitsetupfinished'
	}).then(angular.bind(this, function successCallback(response) {
	    console.log(response.data);
	    if (response.data == 'false') {
	        $('#initSetupModal').modal('show');
            $('#initSetupModal').on('hidden.bs.modal', function (e) {
                $('#initSetupModal').modal('hide');
                console.log('closed');
            })

            $http({
              method: 'GET',
              url: '/funding/getiavtoken'
            }).then(angular.bind(this, function successCallback(response) {
                // this callback will be called asynchronously
                // when the response is available
                this.iavToken = response.data;
                console.log('IAV token fetched: ' + this.iavToken);
                dwolla.configure('uat');
                dwolla.iav.start(this.iavToken, {container: 'initSetupIavContainer'}, angular.bind(this, function(err, res) {
                    console.log('Error: ' + JSON.stringify(err) + ' -- Response: ' + JSON.stringify(res));
                    if (!err) {
                        // Funding IAV successful
                        $('#initSetupNextButton').show();
                        $('#initSetupSkipButton').show();
                    }
                }));
            }), function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
                console.log(response);
            });

            this.http_({
              method: 'POST',
              url: '/login/setinitsetupfinished'
            }).then(angular.bind(this, function successCallback(response) {
            }), function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
                console.log(response);
            });
	    } else {
            $('#initSetupModal').remove();
	    }
	}), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	});

    self.cancel = function() {
        self.dismiss({$value: 'cancel'});
    }
    this.$onInit = function() {
        this.dateOfBirthPickerOpened = false;
    };
};


InitSetupComponentController.prototype.handleNext = function(skip) {
    console.log('next');
	var curContent = $(".init-setup.form-content.current");
	var curNav = $(".init-setup.form-nav.current");
	if (skip) {
	    if (curNav.attr('id') === "navStep3") {
		    this.cancel();
	    } else {
            this.moveToNext(curContent, curNav);
	    }
	} else if (curNav.attr('id') === "navStep1" || this.validateCurrentForm()) {
        if (curNav.attr('id') === "navStep2") {

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
                angular.bind(this, function (response) {
                    console.log('post suceeded');
                    this.getPrograms();
                    this.moveToNext(curContent, curNav);
                }),
                function (response) {
                    console.log('post failed');
                    alert("Something is wrong with the saving. Please try again later");
                }
            );
        } else {
            this.moveToNext(curContent, curNav);
        }
    }
};

InitSetupComponentController.prototype.getPrograms = function() {
    this.http_({
        method: 'GET',
        url: '/manageprogram/listprograms'
    }).then(angular.bind(this, function successCallback(response) {
        // this callback will be called asynchronously
        // when the response is available
        this.programs = [];
        angular.forEach(response.data, angular.bind(this, function(program) {
            this.programs.push(JSON.parse(program));
        }));
    }), angular.bind(this, function errorCallback(response) {
        // TODO(zilong): deal with error here
    }));
};

InitSetupComponentController.prototype.onSaveChildEnrollmentInfo = function(isSaved) {
    this.isDone = isSaved;
}

InitSetupComponentController.prototype.handleDone = function() {
    console.log('done');
    console.log('$ctrl.newChildEnrollmentInfo: ' + this.newChildEnrollmentInfo);
    var submittingForm = angular.copy(this.newChildEnrollmentInfo);
    this.http_.post('/child/add', submittingForm).then(function successCallback(response) {
        var isSaveSuccess = false;
        console.log(response);
        if (response.data.status == 'success') {
            isSaveSuccess = true;
        }
        if (!isSaveSuccess) {
            console.log("Something is wrong with the saving child info. Please try again later");
        }
    }, function errorCallback(response) {
        console.log("Something is wrong with the saving child info. Please try again later");
    });

    this.http_({
	  method: 'POST',
	  url: '/login/setinitsetupfinished'
	}).then(angular.bind(this, function successCallback(response) {
		location.reload();
	}), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	});
};


InitSetupComponentController.prototype.moveToNext = function(curContent, curNav) {
	  curNav.removeClass("current");
	  curNav.next().addClass("current");
	  curNav.next().addClass("active");

	  curContent.removeClass("current");
	  curContent.next().addClass("current");

	  if (curNav.next().attr('id') === "navStep3") {
		  $("#initSetupSkipButton").hide();
		  $("#initSetupNextButton").hide();
		  $("#initSetupDoneButton").show();
	  } else {
		  $("#initSetupNextButton").show();
		  $("#initSetupDoneButton").hide();
	  }
}

InitSetupComponentController.prototype.validateCurrentForm = function() {
	var curContent = $(".init-setup.form-content.current");

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