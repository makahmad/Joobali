
ProgramController = function($scope, $http) {
	console.log('haha1');
	this.scope_ = $scope;
    $scope.num = 0;
    $scope.programs = [{"name":"haha", "fee":"12"}, {"name":"123123123", "fee":"13"}];
	console.log('haha1');
    this.addProgram();

    $http({
	  method: 'GET',
	  url: '/manageprogram/listprograms'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    console.log(response);
	    this.scope_.programs = [];
	    angular.forEach(response.data, angular.bind(this, function(program) {
	    	this.scope_.programs.push(JSON.parse(program));
	    }));
	    console.log(this.scope_.programs);

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
};

ProgramController.prototype.addProgram = function() {
	console.log('haha2');
	this.scope_.programs.push({"name":"test", "fee":"3333"});
};




app = angular.module('programApp', []);
app.controller('ProgramCtrl', ProgramController);
