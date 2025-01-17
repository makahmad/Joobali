ProfileComponentController = function($scope, $http, $window, $sce) {
//    console.log('ProfileComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.profile = {};
	this.emailError = false;
	this.scope_ = $scope;
	this.scope_.newImageSelected = false;
    this.dateOfBirthPickerOpened = false;
    this.today = new Date();
    this.dateFormat = "MM/DD/YYYY";

    this.scope_.htmlTooltip = '';

    this.scope_.fileNameChanged = function() {
        $scope.newImageSelected = true;
    }

    if (angular.equals(this.profile, {})) {
    	$http({
            method: 'GET',
            url: '/profile/getprofile'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available

            this.profile = JSON.parse(response.data[0]);
            this.profile.dateOfBirth = moment(this.profile.dateOfBirth, this.dateFormat).toDate()
        }), function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response);
        });
    }




        function isSatisfied(criteria) {
              return criteria ? 1 : 0;
            }

            function createPasswordTooltip(newVal) {

                tooltip = 'Valid Password:';

                minEightChars = isSatisfied(newVal && newVal.length >= 8);
                minDigit = isSatisfied(newVal && /\d/.test(newVal));
                minCapital = isSatisfied(newVal && /[A-Z]/.test(newVal));
                minLower =  isSatisfied(newVal && /[a-z]/.test(newVal));
                minSpecial = isSatisfied(newVal && /(?=.*\W)/.test(newVal));

                if(minEightChars==1)
                    tooltip +='<div><i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i> Minimum Length of 8</div>';
                else
                    tooltip +='<div><i ng-show="minEightChars==0" class="fa fa-circle-o"></i> Minimum Length of 8</div>';

                if(minSpecial==1)
                    tooltip +='<div><i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i> 1 Special Character</div>';
                else
                    tooltip +='<div><i ng-show="minEightChars==0" class="fa fa-circle-o"></i> 1 Special Character</div>';

                if(minCapital==1)
                    tooltip +='<div><i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i> 1 Capital Letter</div>';
                else
                    tooltip +='<div><i ng-show="minEightChars==0" class="fa fa-circle-o"></i> 1 Capital Letter</div>';

                if(minLower==1)
                    tooltip +='<div><i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i> 1 Lowercase Letter</div>';
                else
                    tooltip +='<div><i ng-show="minEightChars==0" class="fa fa-circle-o"></i> 1 Lowercase Letter</div>';

                if(minDigit==1)
                    tooltip +='<div><i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i> 1 Number</div>';
                else
                    tooltip +='<div><i ng-show="minEightChars==0" class="fa fa-circle-o"></i> 1 Number</div>';

              return tooltip;
            }



          this.scope_.$watch('$ctrl.profile.newPassword', function(newVal) {

            $scope.htmlTooltip = $sce.trustAsHtml( createPasswordTooltip(newVal) );
          });
};

ProfileComponentController.prototype.openDateOfBirthPicker = function() {
        this.dateOfBirthPickerOpened = true;
}
ProfileComponentController.prototype.saveProfile = function() {
    submitting_profile = angular.copy(this.profile)

    if (submitting_profile.dateOfBirth!=null)
        submitting_profile.dateOfBirth = moment(submitting_profile.dateOfBirth).format("MM/DD/YYYY");

	this.http_({
		method: 'POST',
		url: '/profile/updateprofile',
		data: JSON.stringify(submitting_profile)
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
//        console.log('post suceeded');


        if(this.profile.logo)
        {
        	this.http_({
                method: 'POST',
                url: '/profile/updatelogo',
                data: this.profile.logo
            }).then(angular.bind(this, function successCallback(response) {
                // this callback will be called asynchronously
                // when the response is available
//                console.log('logo post suceeded');
                location.reload();

              }), angular.bind(this, function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
                    console.log('logo post failed');

                     bootbox.alert("Something is wrong with the saving. Please try again later");
              }));
        }
        else
            location.reload();


	  }), angular.bind(this, function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
//			console.log('post failed');

			if (response.data=="email already exists")
                 this.emailError = true;
			else if (response.data=="current password is incorrect")
                 this.currentPasswordError = true;
			else
			    bootbox.alert("Something is wrong with the saving. Please try again later");
	  }));
};

ProfileComponentController.prototype.deleteLogo = function() {
	this.http_({
		method: 'POST',
		url: '/profile/updatelogo',
		data: this.profile.logo
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
//        console.log('post suceeded');
        location.reload();


	  }), angular.bind(this, function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
			console.log('post failed');
			alert("Something is wrong with the saving. Please try again later");
	  }));
};

ProfileComponentController.prototype.validateEmail = function() {
    this.emailError = false;

    if (this.profile.email!=null)
    {
        this.http_({
            method: 'POST',
            url: '/profile/validateemail',
            data: JSON.stringify(this.profile.email)
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
//            console.log('email valid ');
            this.emailError = false;

          }), angular.bind(this, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
//                console.log('email invalid');
                this.emailError = true;
          }));

	  }
};

ProfileComponentController.prototype.dwollaFieldsFilled = function(markError) {
    var content = $(".profileContent");

  	var inputs = content.find("input.dwolla-verify"),
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
    return isValid
};

ProfileComponentController.prototype.dwollaVerify = function(markError) {
    submitting_profile = angular.copy(this.profile)
    submitting_profile.dateOfBirth = moment(submitting_profile.dateOfBirth).format("MM/DD/YYYY");
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
                bootbox.alert("Verification Succeeded.")
                location.reload();
            } else {
                bootbox.alert(response.data);
            }

          }), angular.bind(this, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
                bootbox.alert("Something is wrong with the verification. Please try again later");
          }));
    }
};
