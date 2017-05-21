InitSetupComponentController = function($http) {
    console.log('InitSetupComponentController running');
    this.dateOfBirthPickerOpened = false;

    this.openDateOfBirthPicker = function() {
        console.log("Toggle Date picker: " + this.dateOfBirthPickerOpened);
        this.dateOfBirthPickerOpened = ! this.dateOfBirthPickerOpened;
    };

    this.http_ = $http;

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
};


InitSetupComponentController.prototype.getAutopayData = function() {
	this.http_({
	  method: 'GET',
	  url: '/parent/getautopaydata'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.data = JSON.parse(response.data);
	    console.log(this.data);
	    console.log(this.data.providerName);
        this.data.dayNums = [];
        if (this.data.billingFrequency == 'Weekly') {
            for (var i = 0; i <= 7; i++) {
               this.data.dayNums.push('' + i);
            }
        } else {
            for (var i = 0; i <= 30; i++) {
               this.data.dayNums.push('' + i);
            }
        }
        this.data.payDaysBefore = '0';
        this.data.bankAccountId = this.data.bankAccounts[0].id;
        this.data.bankAccountName = this.data.bankAccounts[0].name;
	}), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	});
}

InitSetupComponentController.prototype.handleNext = function(skip) {
    console.log('next');
	var curContent = $(".init-setup.form-content.current");
	var curNav = $(".init-setup.form-nav.current");
    var curTitle = $(".init-setup.modal-title.current");

    console.log(skip);
    if (curNav.attr('id') === "navStep1") {
        this.getAutopayData();
    }
    if (!skip && curNav.attr('id') === "navStep2") {
        // TODO(rongjian): add logic to setup autopay.
        console.log(this.data);
        request = {
            'payDaysBefore': this.data.payDaysBefore,
            'bankAccountId': this.data.bankAccountId,
        }
        success = true;
        this.http_({
          method: 'POST',
          url: '/enrollment/setupautopay',
          data: JSON.stringify(request)
        }).then(
            function(response){
                console.log('post suceeded');
                console.log(response);
                if (response.data !== 'success') {
                    alert(response.data);
                }
            },
            function(response){
                console.log('post failed');
                console.log(response);
                success = false;
            }
         );
        if (!success) {
            return;
        }
    }
    this.moveToNext(curContent, curNav, curTitle);
};


InitSetupComponentController.prototype.handleDone = function() {
    console.log('done');


    this.http_({
	  method: 'POST',
	  url: '/login/setinitsetupfinished'
	}).then(angular.bind(this, function successCallback(response) {
        $('#initSetupModal').modal('hide');
		location.reload();
	}), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	});
};


InitSetupComponentController.prototype.moveToNext = function(curContent, curNav, curTitle) {
	  curNav.removeClass("current");
	  curNav.next().addClass("current");
	  curNav.next().addClass("active");

	  curContent.removeClass("current");
	  curContent.next().addClass("current");

	  curTitle.removeClass("current");
	  curTitle.next().addClass("current");

	  if (curNav.next().attr('id') === "navStep3") {
		  $("#initSetupNextButton").hide();
		  $("#initSetupDoneButton").show();
		  $("#initSetupSkipButton").hide();
	  } else {
		  $("#initSetupNextButton").show();
		  $("#initSetupDoneButton").hide();
		  $("#initSetupSkipButton").show();
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