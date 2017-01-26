ProfileComponentController = function($http, $window) {
    console.log('ProfileComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.profile = {};

    if (angular.equals(this.profile, {})) {
    	$http({
            method: 'GET',
            url: '/profile/getprofile'
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
		url: '/profile/updateprofile',
		data: JSON.stringify(this.profile)
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
