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
            this.enrollmentDetail = angular.fromJson(response.data)[0];
            console.log(this.enrollmentDetail);
        }), function errorCallback(response) {})
}

EnrollmentParentViewController.prototype.$onInit = function() {
    this.enrollmentId = this.routeParams_.enrollmentId;
    this.providerId = this.routeParams_.providerId;
    this.getEnrollmentDetail();
}

EnrollmentParentViewController.prototype.acceptEnrollment = function() {
    request = {
        'enrollment_id' : this.enrollmentId,
        'provider_id' : this.providerId
    };
    this.http_
        .post('/enrollment/accept', request)
        .then(angular.bind(this, function successCallback(response){
            this.getEnrollmentDetail();
        }), function errorCallback(response){});
}

EnrollmentParentViewController.prototype.isWaitingAcceptance = function() {
    return (this.enrollmentDetail == null
            || this.enrollmentDetail.enrollment.status == 'initialized'
            || this.enrollmentDetail.enrollment.status == 'invited');
}