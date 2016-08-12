
FundingController = function($scope, $http) {
	this.scope_ = $scope;

    $http({
	  method: 'GET',
	  url: '/funding/listfundings'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    console.log(response);
	    this.scope_.fundings = [];
	    angular.forEach(response.data, angular.bind(this, function(funding) {
	    	this.scope_.fundings.push(JSON.parse(funding));
	    }));
	    console.log(this.scope_.fundings);

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
};




app = angular.module('fundingApp', []);
app.controller('FundingCtrl', FundingController);
