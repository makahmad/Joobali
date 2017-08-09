InitSetupComponentController = function($http, $location) {
    console.log('InitSetupComponentController running');
    console.log(this.programs);
    this.isDone = false;
    this.location_ = $location;
    self = this

	self.programs = [];
	self.fundings = [];
	self.numberOfChildren = 0;
    this.http_ = $http;
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
                dwolla.configure((window.location.hostname.indexOf('joobali-prod') != -1 || window.location.hostname.indexOf('joobali.com') != -1) ? 'prod' : 'sandbox');
                dwolla.iav.start(this.iavToken,
                    {
                      container: 'initSetupIavContainer',
                      stylesheets: [
                        'https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext',
                      ],
                      microDeposits: true,
                      fallbackToMicroDeposits: true,
                      backButton: true,
                      subscriber: function(currentPage, error) {
                          console.log('currentPage:', currentPage, 'error:', JSON.stringify(error))
                      }
                    },
                    angular.bind(this, function(err, res) {
                        console.log('Error: ' + JSON.stringify(err) + ' -- Response: ' + JSON.stringify(res));
                        if (!err) {
                            // Funding IAV successful
                            $('#initSetupNextButton').show();
                            $('#initSetupSkipButton').hide();
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
	    if (curNav.attr('id') === "navStep2") {
		    this.cancel();
	    } else {
	        this.isDone = true;
            this.moveToNext(curContent, curNav);
	    }
	} else if (curNav.attr('id') === "navStep1" || this.validateCurrentForm()) {
	    this.isDone = true;
        this.moveToNext(curContent, curNav);
    }
};

InitSetupComponentController.prototype.checkList = function() {

    this.http_({
	  method: 'GET',
	  url: '/profile/getdwollastatus'
	}).then(angular.bind(this, function successCallback(response) {
	    this.dwollaStatus = response.data;
	}), function errorCallback(response) {
	    // Do nothing
	});
	this.http_({
		method: 'GET',
		url: '/manageprogram/listprograms'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.programs = [];
	    angular.forEach(response.data, angular.bind(this, function(program) {
            program = JSON.parse(program);
            if(program.indefinite)
                program.endDate = "Indefinite";
	    	this.programs.push(program);
	    }));

	}), function errorCallback(response) {
		// called asynchronously if an error occurs
		// or server returns response with an error status.
		console.log(response);
	});
	this.http_({
	  method: 'GET',
	  url: '/funding/listfunding'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.fundings = [];
	    angular.forEach(response.data, angular.bind(this, function(funding) {
	    	this.fundings.push(JSON.parse(funding));
	    }));

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
	this.http_({
	  method: 'GET',
	  url: '/child/list?'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.numberOfChildren = 0;

	    angular.forEach(response.data, angular.bind(this, function(funding) {
	    	this.numberOfChildren +=1;
	    }));

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
}
InitSetupComponentController.prototype.handleDone = function() {
    console.log('done');

    this.http_({
	  method: 'POST',
	  url: '/login/setinitsetupfinished'
	}).then(angular.bind(this, function successCallback(response) {
	    window.location.href = '/home/dashboard#!/verification';
	    window.location.reload();
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

	  if (curNav.next().attr('id') === "navStep2") {
	      this.checkList();
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