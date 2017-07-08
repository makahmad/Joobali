AddFundingIavComponentController = function($location, $http) {
    console.log('AddFundingIavComponentController running');
    this.location_ = $location;
    self = this

    $http({
	  method: 'GET',
	  url: '/funding/getiavtoken'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.iavToken = response.data;
	    console.log('IAV token fetched: ' + this.iavToken);
        dwolla.configure((window.location.hostname.indexOf('joobali-prod') != -1 || window.location.hostname.indexOf('joobali.com')) != -1 ? 'prod' : 'sandbox');
	        // If element exists. Sometime if the user move to another tab before this callback is called, the iavContainer element will be absent.
        dwolla.iav.start(this.iavToken, {container: 'addFundingIavContainer'}, function(err, res) {
            console.log('Error: ' + JSON.stringify(err) + ' -- Response: ' + JSON.stringify(res));
            if (!err) {
                location.reload();
            }
        });

	}), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	});

    self.cancel = function() {
        self.dismiss({$value: 'cancel'});
    }
}
