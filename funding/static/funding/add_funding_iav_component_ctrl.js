AddFundingIavComponentController = function($location, $http) {
    console.log('AddFundingIavComponentController running');
    this.location_ = $location;
    self = this;
    self.success = false;

    $http({
	  method: 'GET',
	  url: '/funding/getiavtoken'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.iavToken = response.data;
	    console.log('IAV token fetched: ' + this.iavToken);
        dwolla.configure((window.location.hostname.indexOf('joobali-prod') != -1 || window.location.hostname.indexOf('joobali.com') != -1) ? 'prod' : 'sandbox');
	        // If element exists. Sometime if the user move to another tab before this callback is called, the iavContainer element will be absent.
        dwolla.iav.start(this.iavToken,
            {
              container: 'addFundingIavContainer',
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
            function(err, res) {
                console.log('Error: ' + JSON.stringify(err) + ' -- Response: ' + JSON.stringify(res));
                if (!err) {
                    self.success = true;
                }
            });

	}), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	});

    self.cancel = function() {
        self.dismiss({$value: 'cancel'});
        if (self.success) {
            location.reload();
        }
    }
}
