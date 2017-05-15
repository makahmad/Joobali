EnrollmentParentViewController = function EnrollmentParentViewController($http, $routeParams, $location, $timeout) {
    this.http_ = $http;
    this.routeParams_ = $routeParams;
    this.location_ = $location;
    this.timeout_ = $timeout;

    this.showSuccessAlert = false;
    this.showFailureAlert = false;
    this.counter = 5;
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
            this.showSuccessAlert = true;
            this.showFailureAlert = false;
            this.redirectToFirstInvoice();
            this.getEnrollmentDetail();
        }), angular.bind(this, function errorCallback(response){
            this.showSuccessAlert = false;
            this.showFailureAlert = true;
        }));
}


EnrollmentParentViewController.prototype.redirectToFirstInvoice = function () {
    // TODO(rongjian): redirect to specific invoice instead of general 'invoices' page
    this.counter--;
    if (this.counter == 0) {
        this.location_.path("due");
    } else {
        this.timeout_(angular.bind(this, this.redirectToFirstInvoice), 1000);
    }
}

EnrollmentParentViewController.prototype.isWaitingAcceptance = function() {
    return (this.enrollmentDetail == null
            || this.enrollmentDetail.enrollment.status == 'initialized'
            || this.enrollmentDetail.enrollment.status == 'invited');
}