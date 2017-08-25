ProfileComponentController = function($scope, $http, $window, $sce) {
    console.log('ProfileComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.profile = {};
	this.emailError = false;
	this.disableSave = false;
	this.scope_ = $scope;
    this.scope_.htmlTooltip = '';

    if (angular.equals(this.profile, {})) {
    	$http({
            method: 'GET',
            url: '/parent/getprofile'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available

            this.profile = JSON.parse(response.data[0]);

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

ProfileComponentController.prototype.saveProfile = function() {
	this.http_({
		method: 'POST',
		url: '/parent/updateprofile',
		data: JSON.stringify(this.profile)
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
        console.log('post suceeded');
        location.reload();

	  }), angular.bind(this, function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
			console.log('post failed');

			if (response.data=="email already exists")
                 this.emailError = true;
			else if (response.data=="current password is incorrect")
                 this.currentPasswordError = true;
			else
			    bootbox.alert("Something is wrong with the saving. Please try again later");
	  }));
};


ProfileComponentController.prototype.validateEmail = function() {
    this.emailError = false;

    if (this.profile.email!=null)
    {
        this.http_({
            method: 'POST',
            url: '/parent/validateemail',
            data: JSON.stringify(this.profile.email)
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            console.log('email valid ');
            this.disableSave = false;
            this.emailError = false;

          }), angular.bind(this, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
                console.log('email invalid');
                this.disableSave = true;
                this.emailError = true;
          }));

	  }
};

