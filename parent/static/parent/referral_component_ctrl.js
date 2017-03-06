ReferralComponentController = function($http, $window, $location) {
    console.log('ReferralComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.referral = {};
    this.sent = false;

    this.cancel = function () {
      this.dismiss({$value: 'cancel'});
    };
};


ReferralComponentController.prototype.refer = function() {
	this.http_({
		method: 'POST',
		url: '/referral/providerreferral',
		data: JSON.stringify(this.referral)
	}).then(
		angular.bind(this, function (response) {
			console.log('post suceeded');
            this.sent = true;
            //this.close({$value : this.referral});

		}),
		function (response) {
			console.log('post failed');
			alert("Something is wrong with the saving. Please try again later");
		}
	);
};

