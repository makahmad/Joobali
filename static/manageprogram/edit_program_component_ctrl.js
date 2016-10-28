var TIME_FORMAT =  'hh:mm A';

EditProgramComponentController = function($scope, $http, $window) {
    console.log('EditProgramComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.scope_ = $scope;

};