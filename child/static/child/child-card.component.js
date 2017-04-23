ChildCardController = function ChildCardController($uibModal, $scope, $http, $routeParams, $location) {
    this.uibModal_ = $uibModal;
    this.scope_ = $scope;
    this.http_ = $http;
    this.routeParams_ = $routeParams;
    this.location_ = $location;
}

ChildCardController.prototype.$onInit = function() {
    this.getEnrollmentData();
    console.log(moment(this.child.date_of_birth, "MM/DD/YYYY").toNow(true));
    var currentDate = moment(new Date());
    var dateDiff = moment.duration(currentDate.diff(moment(this.child.date_of_birth, "MM/DD/YYYY")));
    diff_str = "";
    if (dateDiff.years() > 0) {
        diff_str += dateDiff.years() + " years, "
    }
    if (dateDiff.months() > 0) {
        diff_str += dateDiff.months() + " months, "
    }
    if (dateDiff.days() > 0) {
        diff_str += dateDiff.days() + " days"
    }
    this.child.age = diff_str;
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
        angular.forEach(response.data, angular.bind(this, function(enrollment) {
            this.enrollments.push(JSON.parse(enrollment));
        }));
    }), angular.bind(this, function errorCallback(response){
    }));
};