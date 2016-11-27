InitSetupComponentController = function($http) {
    console.log('InitSetupComponentController running');
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
                    }
                }));
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


};


InitSetupComponentController.prototype.handleNext = function() {
    console.log('next');
	var curContent = $(".init-setup.form-content.current");
	var curNav = $(".init-setup.form-nav.current");
    if (curNav.attr('id') === "navStep1" || this.validateCurrentForm()) {
        if (curNav.attr('id') === "navStep2") {
            console.log(this.newProgram);
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


InitSetupComponentController.prototype.handleDone = function() {
    console.log('done');
    // TODO: save the last task (i.e. add child)
    this.http_({
	  method: 'POST',
	  url: '/login/setinitsetupfinished'
	}).then(angular.bind(this, function successCallback(response) {
        $('#initSetupModal').modal('hide');
        //$('#initSetupModal').remove();
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