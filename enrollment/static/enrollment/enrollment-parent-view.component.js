EnrollmentParentViewController = function EnrollmentParentViewController($uibModal, $log, $http, $routeParams, $location, $timeout) {
//    console.log('in EnrollmentParentViewController');
    this.uibModal_ = $uibModal;
    this.http_ = $http;
    this.routeParams_ = $routeParams;
    this.location_ = $location;
    this.timeout_ = $timeout;
    this.log_ = $log;

    this.showSuccessAlert = false;
    this.showFailureAlert = false;
    this.counter = 5;

    this.enrollmentMap = {
    'initialized':'Invited (but not accepted)',
    'cancel':'Canceled',
    'inactive':'Inactive',
    'active':'Active',
    'invited':'Invited (but not accepted)'};
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

            //
            // if(enrollment.enrollment.sent_email_count==0 && enrollment.enrollment.status=='initialized')
            //     enrollment.enrollment.status = 'pre-initialized'
            //
            // this.enrollments.push(enrollment);

            if (this.enrollmentDetail.enrollment==null)
            {
                bootbox.alert("The program does not exist or has been removed by the provider."+
                    "<br>Please go to the Children page and review your child's other programs.");
                this.location_.path('/child/list');
			}

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


EnrollmentParentViewController.prototype.cancelAutoPay = function() {




        bootbox.confirm({
        message: "Are you sure you want to cancel autopay?",
        buttons: {
            confirm: {
                label: 'Yes',
                className: 'btn btn-default btn-lg pull-right joobali'
            },
            cancel: {
                label: 'No',
				className: 'btn btn-default btn-lg pull-right'
            }
        },
        callback: angular.bind(this, function(result) {
            if (result === true) {
//                console.log('canceling autopay');
//    console.log(this.enrollmentDetail);


                this.http_({
                  method: 'POST',
                  url: '/enrollment/cancelAutopay',
                  data: JSON.stringify(this.enrollmentDetail)
                })
                .then(
                    angular.bind(this, function(response){
                        if (response.data !== 'success') {
                            bootbox.alert(response.data);
                        } else {
                            bootbox.alert("Autopay cancelled successfully.", function() {
                                location.reload();
                            });
                        }
                    }),
                    angular.bind(this, function(response){
                        bootbox.alert(response.data);
                    })
                 );
            }
        })
    });
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
            || this.enrollmentDetail.enrollment == null
            || this.enrollmentDetail.enrollment.status == 'initialized'
            || this.enrollmentDetail.enrollment.status == 'invited');
}

EnrollmentParentViewController.prototype.isOnAutoPay = function() {
    return ( this.enrollmentDetail!=null && this.enrollmentDetail.enrollment.autopay_source_id != null);
}