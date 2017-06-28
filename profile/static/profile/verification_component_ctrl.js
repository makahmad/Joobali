VerificationComponentController = function($scope, $http, $window, $sce) {
    console.log('VerificationComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.profile = {};
	this.scope_ = $scope;
    this.dateOfBirthPickerOpened = false;
    this.today = new Date();
    this.dateFormat = "MM/DD/YYYY"

    if (angular.equals(this.profile, {})) {
    	$http({
            method: 'GET',
            url: '/profile/getprofile'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available

            this.profile = JSON.parse(response.data[0]);
            console.log(this.profile);
            this.profile.dateOfBirth = moment(this.profile.dateOfBirth, this.dateFormat).toDate();

            //redirect provider to home if they are already verified
//            if(this.profile.dwolla_status=='verified')
//                window.location = "/home/dashboard#!/home";
        }), function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response);
        });
    }

};

VerificationComponentController.prototype.openDateOfBirthPicker = function() {
        this.dateOfBirthPickerOpened = true;
}

VerificationComponentController.prototype.dwollaFieldsFilled = function(markError) {
    var content = $(".verifyContent");

  	var inputs = content.find("input.dwolla-verify");
  	isValid = true;


	$(".form-group").removeClass("has-error");
	for(var i=0; i< inputs.length; i++){
		if (!inputs[i].value){
			isValid = false;
			if (markError) {
                $(inputs[i]).closest(".form-group").addClass("has-error");
			}
		}
	}
  	var inputs = content.find("select.dwolla-verify");
	for(var i=0; i< inputs.length; i++){

		if (inputs[i].value.length != 2){
			isValid = false;
			if (markError) {
                $(inputs[i]).closest(".form-group").addClass("has-error");
			}
		}
	}
    return isValid
};

VerificationComponentController.prototype.dwollaVerify = function(markError) {
    submitting_profile = angular.copy(this.profile)
    if (submitting_profile.dateOfBirth!=null)
    submitting_profile.dateOfBirth = moment(submitting_profile.dateOfBirth).format("MM/DD/YYYY");

    if (this.profile.dwolla_status != 'verified') {
        if (this.profile.dwolla_status == 'document') {
            if(this.profile.doc) {
                    var fd = new FormData();
                    //Take the first selected file
                    fd.append("file", this.profile.doc);

                    this.http_.post('/profile/updatedoc', fd, {
                        withCredentials: true,
                        headers: {'Content-Type': undefined },
                        transformRequest: angular.identity
                    }).then(angular.bind(this, function successCallback(response) {
                        // this callback will be called asynchronously
                        // when the response is available
                        console.log('logo post suceeded');
                        location.reload();

                      }), angular.bind(this, function errorCallback(response) {
                        // called asynchronously if an error occurs
                        // or server returns response with an error status.
                            console.log('logo post failed');

                             alert("Something is wrong with the saving. Please try again later");
                      }));
            }
        } else {
            if (this.dwollaFieldsFilled(markError)) {
                this.http_({
                    method: 'POST',
                    url: '/profile/dwollaverify',
                    data: JSON.stringify(submitting_profile)
                }).then(angular.bind(this, function successCallback(response) {
                    // this callback will be called asynchronously
                    // when the response is available
                    if (response.data == 'success') {
                        this.profile.dwolla_status = 'verified'
                        alert("Verification Succeeded.")
                        location.reload();
                    } else {
                        alert(response.data);
                    }

                  }), angular.bind(this, function errorCallback(response) {
                    // called asynchronously if an error occurs
                    // or server returns response with an error status.
                        alert("Something is wrong with the verification. Please try again later");
                  }));
            }
        }
    }
};

VerificationComponentController.prototype.deleteDoc = function() {
    var fd = new FormData();
    //Take the first selected file
    fd.append("file", this.profile.doc);

    this.http_.post('/profile/updatedoc', fd, {
        withCredentials: true,
        headers: {'Content-Type': undefined },
        transformRequest: angular.identity
    }).then(angular.bind(this, function successCallback(response) {
        // this callback will be called asynchronously
        // when the response is available
        console.log('logo post suceeded');
        location.reload();

      }), angular.bind(this, function errorCallback(response) {
        // called asynchronously if an error occurs
        // or server returns response with an error status.
            console.log('logo post failed');

             alert("Something is wrong with the saving. Please try again later");
      }));
};

VerificationComponentController.prototype.getDocName = function() {
    var fullPath = document.getElementById('verification_doc').value;
    if (fullPath) {
        var startIndex = (fullPath.indexOf('\\') >= 0 ? fullPath.lastIndexOf('\\') : fullPath.lastIndexOf('/'));
        var filename = fullPath.substring(startIndex);
        if (filename.indexOf('\\') === 0 || filename.indexOf('/') === 0) {
            filename = filename.substring(1);
        }
        return filename;
    }
    return null;
}