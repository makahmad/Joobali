
EnrollmentController = function($scope, $http) {
	console.log('EnrollmentController running');
	this.scope_ = $scope;
    $scope.num = 0;
	console.log($scope);
    this.addEnrollment();

    $http({
	  method: 'GET',
	  url: '/enrollment/list'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    console.log(response);
	    this.scope_.enrollments = [];
	    angular.forEach(response.data, angular.bind(this, function(enrollment) {
	    	this.scope_.enrollments.push(JSON.parse(enrollment));
	    }));
	    console.log(this.scope_.enrollments);

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
};

EnrollmentController.prototype.addEnrollment = function() {
    console.log("EnrollmentController.protoType.addEnrollment()");
};

app = angular.module('enrollmentApp', []);
app.controller('EnrollmentCtrl', EnrollmentController);
