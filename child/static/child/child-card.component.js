ChildCardController = function ChildCardController($uibModal, $scope, $http, $routeParams, $location) {

    var self = this;
    self.openEnrollmentModal = function() {
        console.log("Opening Add Enrollment Modal");
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: '/static/child/child-enrollment.template.html',
            controller: 'ChildEnrollmentController',
            controllerAs: '$ctrl',
            resolve: {
                child: function () {
                    return self.child;
                },
                programs: function() {
                    return self.programs;
                }
            }
        });
    };

    // TODO(zilong): Move this to ChildListController
    self.getProgramData = function() {
        $http({
            method: 'GET',
            url: '/manageprogram/listprograms'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            this.programs = [];
            angular.forEach(response.data, angular.bind(this, function(program) {
                this.programs.push(JSON.parse(program));
            }));
        }), function errorCallback(response) {
            // TODO(zilong): deal with error here
        });
    };

    self.getEnrollmentData = function() {
        $http.post('/enrollment/listByChildId', { 'child_id' : this.child.id })
        .then(angular.bind(this, function successCallback(response) {
            this.enrollments = [];
            console.log('enrollment/listByChild: ' + response.data)
            angular.forEach(response.data, angular.bind(this, function(enrollment) {
                this.enrollments.push(JSON.parse(enrollment));
            }));
        }), angular.bind(this, function errorCallback(response){
        }));
    };

    self.$onInit = function() {
        this.getProgramData();
        this.getEnrollmentData();
    };
}
