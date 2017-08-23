EnrollmentAcceptanceDialogController = function EnrollmentAcceptanceDialogController($uibModalInstance, $log, $http, config) {
    this.enrollmentId_ = config.enrollmentId;
    this.providerId_ = config.providerId;
    this.isChildDOBMissing = config.isChildDOBMissing;
    this.http_ = $http;
    this.uibModalInstance_ = $uibModalInstance;
    this.log_ = $log;
    this.dateOfBirthPickerOpened = false;
    this.todayDate = new Date();
    this.enableAutopay = true;
    $log.info("EnrollmentAcceptanceDialogController with: " + angular.toJson(config));
}

EnrollmentAcceptanceDialogController.prototype.$onInit = function () {
    this.getAutopayData();
}

EnrollmentAcceptanceDialogController.prototype.acceptEnrollment = function () {
    var request = {};
    request['enrollment_id'] = this.enrollmentId_;
    request['provider_id'] = this.providerId_;
    if (this.isChildDOBMissing) {
        request['date_of_birth'] = moment(this.child_date_of_birth).format('MM/DD/YYYY');
    }

    if (this.enableAutopay && this.autopayData && this.autopayData.bankAccounts.length > 0) {
        request['autopay_source_id'] = this.autopayData.bankAccounts[0].id;
        request['pay_days_before'] = '0';
    }

    this.http_
        .post('/enrollment/accept', request)
        .then(angular.bind(this, function successCallback(response) {
            var data = {
                showSuccessAlert: true,
                showFailureAlert: false,
                redirectToFirstInvoice: true,
                refreshEnrollmentDetail: true
            };
            this.closeModal(data);
        }), angular.bind(this, function errorCallback(response) {
            var data = {
                showSuccessAlert: false,
                showFailureAlert: true,
                redirectToFirstInvoice: false,
                refreshEnrollmentDetail: false
            };
            this.closeModal(data);
        }));
}

EnrollmentAcceptanceDialogController.prototype.openDateOfBirthPicker = function() {
    this.dateOfBirthPickerOpened = ! this.dateOfBirthPickerOpened;
};

EnrollmentAcceptanceDialogController.prototype.closeModal = function (data) {
    this.uibModalInstance_.close(data);
}

EnrollmentAcceptanceDialogController.prototype.getAutopayData = function() {
	this.http_({
	  method: 'GET',
	  url: '/parent/getautopaydata'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.autopayData = JSON.parse(response.data);
	    console.log(this.autopayData);
	}), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	});
}