ChildFormContentController = function ChildFormContentController($http, EnrollmentDateChecker) {
    this.http_ = $http;
    this.dateOfBirthPickerOpened = false;
    this.startDatePickerOpened = false;
    this.endDatePickerOpened = false;
    this.readOnly = false;
    this.todayDate = new Date();
    this.dateFormat = 'MM/DD/YYYY';
    this.showSaveButton = true;
    this.disableSaveButton = false;
    this.isAddNewParent = (this.emails.length == 0);
    this.newChildEnrollmentInfo = {};
    this.newChildEnrollmentInfo.error = {};
    this.enrollmentDateChecker_ = EnrollmentDateChecker;


    this.enrollmentStatus = '';
    this.enrollmentDatePickerOptions = { // for start date
        minDate: this.todayDate,
        dateDisabled: angular.bind(this, this.enrollmentDisabledDate),
				showWeeks: false
    }

    this.enrollmentEndDatePickerOptions = {
        minDate: this.todayDate,
        dateDisabled: angular.bind(this, this.enrollmentDisabledEndDate)
    }


    this.paymentTypes = [{
      id: 'Cash',
      label: 'Cash'
    }, {
      id: 'Check',
      label: 'Check'
    }, {
      id: 'Other',
      label: 'Other'
    }];
}

ChildFormContentController.prototype.whenSelectedProgramChange = function () {
    if (this.newChildEnrollmentInfo.program) {
        this.newChildEnrollmentInfo.start_date = moment(this.newChildEnrollmentInfo.program.startDate).toDate();
        if (this.newChildEnrollmentInfo.program.endDate) {
            this.newChildEnrollmentInfo.end_date = moment(this.newChildEnrollmentInfo.program.endDate).toDate();
        } else {
            this.newChildEnrollmentInfo.end_date = "";
        }
        this.newChildEnrollmentInfo.fee = this.newChildEnrollmentInfo.program.fee;
    } else {
        this.newChildEnrollmentInfo.start_date = null;
        this.newChildEnrollmentInfo.fee = 0;
    }
    this.whenChangeStartDate();
}

ChildFormContentController.prototype.whenChangeStartDate = function() {
    if (this.newChildEnrollmentInfo.program && this.newChildEnrollmentInfo.program.endDate) {
        this.newChildEnrollmentInfo.end_date = moment(this.newChildEnrollmentInfo.program.endDate).toDate();
    } else {
        this.newChildEnrollmentInfo.end_date = null;
    }
}


// Disable invalid choices for billing end date
ChildFormContentController.prototype.enrollmentDisabledEndDate = function(dateAndMode) {
    return this.enrollmentDateChecker_.isEnrollmentEndDateDisabled(
            dateAndMode, 
            this.newChildEnrollmentInfo.program, 
            this.newChildEnrollmentInfo.start_date);
}

ChildFormContentController.prototype.enrollmentDisabledDate = function(dateAndMode) {
    return this.enrollmentDateChecker_.isEnrollmentDateDisabled(
            dateAndMode, 
            this.newChildEnrollmentInfo.program);
}

ChildFormContentController.prototype.openDateOfBirthPicker = function() {
    this.dateOfBirthPickerOpened = ! this.dateOfBirthPickerOpened;
};

ChildFormContentController.prototype.openStartDatePicker = function() {
    this.startDatePickerOpened = ! this.startDatePickerOpened;
};

ChildFormContentController.prototype.openEndDatePicker = function() {
    this.endDatePickerOpened = ! this.endDatePickerOpened;
};

ChildFormContentController.prototype.openPaymentDatePicker = function() {
    this.paymentDatePickerOpened = true;
}

ChildFormContentController.prototype.save = function() {
    isValid = true;
    angular.forEach(addChildForm, angular.bind(this, function(value, key) {
        if (value.tagName == 'INPUT' || value.tagName == 'SELECT'){
            if(angular.element(value).hasClass('ng-invalid')) {
                this.newChildEnrollmentInfo.error[value.id] = true;
                isValid = false;
            } else {
                this.newChildEnrollmentInfo.error[value.id] = false;
            }
        }
    }));
    if (!isValid) {
        return;
    }

    var submittingForm = angular.copy(this.newChildEnrollmentInfo);
    if (submittingForm.child_date_of_birth) {
        submittingForm.child_date_of_birth = moment(submittingForm.child_date_of_birth).format("MM/DD/YYYY");
    } else {
        submittingForm.child_date_of_birth = '';
    }
    console.log(submittingForm.child_date_of_birth);
    submittingForm.start_date = moment(submittingForm.start_date).format("MM/DD/YYYY");
    submittingForm.end_date = submittingForm.end_date ? moment(submittingForm.end_date).format("MM/DD/YYYY") : "";

    if (submittingForm.payment_date) {
        submittingForm.payment_date = moment(submittingForm.payment_date).format("MM/DD/YYYY");
    } else {
        submittingForm.payment_date = '';
    }
    if (submittingForm.payment_type) {
        submittingForm.payment_type = submittingForm.payment_type.id;
    }

    this.disableSaveButton = true;
    this.http_.post('/child/add', submittingForm).then(angular.bind(this, function successCallback(response) {
        if (response.data.status == 'success') {
            this.enrollmentStatus = 'success';
            this.showSaveButton = false;
            this.onSave({'isSaved': true});
            this.readOnly = true;
        } else {
            this.enrollmentStatus = 'failure';
            this.onSave({'isSaved': false});
            this.readOnly = false;
            this.disableSaveButton = false;
            this.enrollmentFailureReason = response.data;
        }
    }), angular.bind(this, function errorCallback(response) {
        this.enrollmentStatus = 'failure';
        this.onSave({'isSaved': false});
        this.readOnly = false;
        this.enrollmentFailureReason = response.data;
        this.disableSaveButton = false;
    }));
}

ChildFormContentController.prototype.newParentToggle = function() {
    this.isAddNewParent = !this.isAddNewParent;
}

ChildFormContentController.prototype.cancel = function() {
    this.onClose();
}