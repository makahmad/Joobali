ProfileComponentController = function($scope, $http, $window, $sce) {
    console.log('ProfileComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.profile = {};
	this.emailError = false;
	this.disableSave = false;
	this.scope_ = $scope;
    this.scope_.htmlTooltip = $sce.trustAsHtml('<p>Valid Password:</p><ul><li>Min length 8</li>'+
    '<li>Special Character</li><li>Digit</li><li>Capital Letter</li></ul>');

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

