GeneralBillingComponentController = function($scope, $http, $window) {
    console.log('GeneralBillingComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.generalBilling = {};
	this.scope_ = $scope;

    if (angular.equals(this.generalBilling, {})) {
    	$http({
            method: 'GET',
            url: '/funding/getgeneralbilling'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available

            this.generalBilling = JSON.parse(response.data[0]);

        }), function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response);
        });
    }
};


GeneralBillingComponentController.prototype.saveGeneralBilling = function() {

	this.http_({
		method: 'POST',
		url: '/funding/updategeneralbilling',
		data: JSON.stringify(this.generalBilling)
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
        console.log('post suceeded');
        location.reload();

	  }), angular.bind(this, function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
			console.log('post failed');
            alert("Something is wrong with the saving. Please try again later");
	  }));
};
