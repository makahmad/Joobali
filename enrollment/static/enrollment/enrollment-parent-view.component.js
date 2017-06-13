EnrollmentParentViewController = function EnrollmentParentViewController($uibModal, $log, $http, $routeParams, $location, $timeout) {
    this.uibModal_ = $uibModal;
    this.http_ = $http;
    this.routeParams_ = $routeParams;
    this.location_ = $location;
    this.timeout_ = $timeout;
    this.log_ = $log;

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

EnrollmentParentViewController.prototype.openEnrollmentAcceptanceDialog = function() {

    var config = {
        providerId: this.providerId,
        enrollmentId: this.enrollmentId,
        isChildDOBMissing: true
    }

    if (this.enrollmentDetail.child.date_of_birth) {
        config.isChildDOBMissing = false;
    }

    var modalInstance = this.uibModal_.open({
        animation : true, 
        templateUrl: '/static/enrollment/enrollment-acceptance-dialog.template.html',
        controller: 'EnrollmentAcceptanceDialogController',
        controllerAs: '$ctrl',
        resolve: {
            config: function() {return config;}
        }
    })

    modalInstance.result.then(angular.bind(this, function(data) {
        this.log_.info("data is %s", angular.toJson(data));
        if (data.refreshEnrollmentDetail) {
            this.getEnrollmentDetail();
        }
        if (data.redirectToFirstInvoice) {
            this.redirectToFirstInvoice();
        }
    }), angular.bind(this, function() {
        this.log_.info('Modal dismissed at: ' + new Date());
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