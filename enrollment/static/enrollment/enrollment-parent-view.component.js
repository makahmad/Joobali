EnrollmentParentViewController = function EnrollmentParentViewController($http, $routeParams) {
    this.http_ = $http;
    this.routeParams_ = $routeParams;
}

EnrollmentParentViewController.prototype.getEnrollmentDetail = function() {
    request = {
        'enrollments': [
            {'id': this.enrollmentId, 'provider_id' : this.providerId}
        ]
    }
    this.http_
        .post('/enrollment/get', request)
        .then(angular.bind(this, function successCallback(response) {
            this.enrollmentsDetails = angular.fromJson(response.data);
            this.enrollmentDetail = this.enrollmentsDetails[0];
            console.log(this.enrollmentDetail);
        }), function errorCallback(response) {})
}

EnrollmentParentViewController.prototype.$onInit = function() {
    this.enrollmentId = this.routeParams_.enrollmentId;
    this.providerId = this.routeParams_.providerId;
    this.getEnrollmentDetail();
}