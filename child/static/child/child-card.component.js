ChildCardController = function ChildCardController($uibModal, $scope, $http, $routeParams, $location) {
    this.uibModal_ = $uibModal;
    this.scope_ = $scope;
    this.http_ = $http;
    this.routeParams_ = $routeParams;
    this.location_ = $location;
}

ChildCardController.prototype.$onInit = function() {
    this.getEnrollmentData();
    console.log('this.child is ' + this.child);
    console.log('this.programs is ' + this.programs);
};

ChildCardController.prototype.openEnrollmentModal = function() {
    console.log("Opening Add Enrollment Modal");
    var self = this;
    var modalInstance = this.uibModal_.open({
        animation: true,
        templateUrl: '/static/child/child-enrollment.template.html',
        controller: 'ChildEnrollmentController',
        controllerAs: '$ctrl',
        resolve: {
            child: function() {
                return self.child;
            },
            programs: function() {
                return self.programs;
            }
        }
    });
};

ChildCardController.prototype.getChild = function() {
    return this.child;
}

ChildCardController.prototype.getPrograms = function() {
    return this.programs;
}


ChildCardController.prototype.getEnrollmentData = function() {
    this.http_.post('/enrollment/listByChildId', { 'child_id' : this.child.id })
    .then(angular.bind(this, function successCallback(response) {
        this.enrollments = [];
        console.log('enrollment/listByChild: ' + response.data)
        angular.forEach(response.data, angular.bind(this, function(enrollment) {
            this.enrollments.push(JSON.parse(enrollment));
        }));
    }), angular.bind(this, function errorCallback(response){
    }));
};