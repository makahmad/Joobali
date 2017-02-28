

ConfirmDeleteProgramComponentController = function($http, $window, $location) {
    console.log('EditProgramComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.program = {};
    this.location_ = $location;



        var $ctrl = this;

    $ctrl.$onInit = function () {

          	$http({
            method: 'GET',
            url: '/manageprogram/getprogram',
            params: {id: $ctrl.resolve.programId}
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available

            this.program = JSON.parse(response.data[0]);

        }), function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response);
        });

    };

        $ctrl.cancel = function () {
          $ctrl.dismiss({$value: 'cancel'});
        };

};



ConfirmDeleteProgramComponentController.prototype.deleteProgram = function() {
	this.http_({
		method: 'POST',
		url: '/manageprogram/deleteprogram',
		data: JSON.stringify({id: this.program.id})
	}).then(
		angular.bind(this, function (response) {
			console.log('post suceeded');

			//this.window_.location.href = '/home/dashboard';

			this.location_.path('/programs');
			location.reload();

		}),
		function (response) {
			console.log('post failed');
			alert("Something is wrong with the saving. Please try again later");
		}
	);
};