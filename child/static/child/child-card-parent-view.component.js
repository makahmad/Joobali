ChildCardParentViewController = function ChildCardParentViewController($http) {
    this.http_ = $http;
    this.enrollments = [];
}

ChildCardParentViewController.prototype.getEnrollmentData = function() {
    this.http_.post('/enrollment/listByChildId', { 'child_id' : this.child.id })
    .then(angular.bind(this, function successCallback(response) {
        this.enrollments = [];
        angular.forEach(response.data, angular.bind(this, function(enrollment) {
            this.enrollments.push(JSON.parse(enrollment));
        }));
    }), angular.bind(this, function errorCallback(response){
    }));
}

ChildCardParentViewController.prototype.$onInit = function() {
    this.getEnrollmentData();
}