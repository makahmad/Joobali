enrollmentListController = function EnrollmentFormController($http, $location) {
    console.log('EnrollmentFormController running');
    this.enrollmentInfo = {};

    this.headers = [
        'Child First Name',
        'Child Last Name',
        'Email',
    ];

    this.getProgramData = function() {
        $http({
            method: 'GET',
            url: '/manageprogram/listprograms'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            console.log(response);
            this.programs = [];
            angular.forEach(response.data, angular.bind(this, function(program) {
                this.programs.push(JSON.parse(program));
            }));
            console.log(this.programs)
        }), function errorCallback(response) {
            // TODO(zilong): deal with error here
        });
    }

    this.refreshEnrollment = function() {
        $http({
            method: 'GET',
            url: '/enrollment/list'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            console.log(response);
            this.enrollments = [];
            angular.forEach(response.data, angular.bind(this, function(enrollment) {
                this.enrollments.push(JSON.parse(enrollment));
            }));
            console.log(this.enrollments);
        }), function errorCallback(response) {
            // TODO(zilong): deal with error here
            console.log(response);
        });
    };

    this.resetButton = function() {
        $("#nextButton").show();
        $("#saveButton").hide();
        $("#doneButton").hide();
    };

    this.resetSaveResult = function() {
        $("#saveSuccessLabel").addClass('hide');
        $("#saveFailureLabel").addClass('hide');
    }

    this.editView = function(enrollmentId, programId) {
        console.log("enrollmentId: " + enrollmentId + ", programId: " + programId);
        $location.path("/enrollment/edit/" + enrollmentId + "/" + programId);
        console.log($location.path());
    }

    this.$onInit = function() {
        this.refreshEnrollment();
        this.getProgramData();
    }
}