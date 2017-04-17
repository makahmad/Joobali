HelpCenterComponentController = function($scope, $http, $window, $sce) {
    console.log('HelpCenterComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.help = {};
	this.help.sent = false;
	this.scope_ = $scope;

};

HelpCenterComponentController.prototype.sendComments = function() {
	this.http_({
		method: 'POST',
		url: '/helpcenter/sendcomments',
		data: JSON.stringify(this.help)
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
        console.log('post suceeded');

            this.help.sent = true;


	  }), angular.bind(this, function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
			console.log('post failed');
			    alert("Something is wrong with the saving. Please try again later");
	  }));
};