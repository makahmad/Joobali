AddFundingIavComponentController = function($location, $http) {
    console.log('AddFundingIavComponentController running');
    this.location_ = $location;


    $http({
	  method: 'GET',
	  url: '/funding/getiavtoken'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.iavToken = response.data;
	    console.log('IAV token fetched: ' + this.iavToken);
	    dwolla.configure('uat');
	    if (angular.element('#iavContainer').length) {
	        // If element exists. Sometime if the user move to another tab before this callback is called, the iavContainer element will be absent.
            dwolla.iav.start(this.iavToken, {container: 'iavContainer'}, function(err, res) {
                console.log('Error: ' + JSON.stringify(err) + ' -- Response: ' + JSON.stringify(res));
            });
	    }

	}), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	});
}
