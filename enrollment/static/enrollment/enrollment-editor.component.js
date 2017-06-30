EnrollmentEditorController = function EnrollmentEditorController($uibModalInstance, $http, EnrollmentDateChecker, enrollment) {
    this.uibModalInstance_ = $uibModalInstance;
    this.http_ = $http;
    this.enrollmentDateChecker_ = EnrollmentDateChecker;

    this.enrollment = enrollment;
    this.enrollment.start_date = moment(enrollment.start_date).toDate();
    this.enrollment.start_date_str = moment(enrollment.start_date).format("LL");
    this.enrollment.end_date = moment(enrollment.end_date).toDate();
    this.enrollment.end_date_str = moment(enrollment.end_date).format("LL");

    this.newEnrollment = angular.copy(enrollment);

    this.startDatePickerOpened = false;
    this.endDatePickerOpened = false;

    this.child = {};
    this.program = {};
    this.currentStep = 0;
    this.todayDate = Date();
    this.enrollmentDatePickerOptions = {
        minDate: this.todayDate,
        dateDisabled: angular.bind(this, this.enrollmentDisabledDate)
    }
    
    this.enrollmentEndDatePickerOptions = {
        minDate: this.todayDate,
        dateDisabled: angular.bind(this, this.enrollmentDisabledEndDate)
    }
}

EnrollmentEditorController.prototype.renderEnrollmentEditor = function(enrollment) {
  var child_key = enrollment.child_key;
  var child_id = child_key.Child;
  var get_child_request = {'child_id' : child_id};

  this.http_.post('/child/get', get_child_request)
  .then(angular.bind(this, function successCallback(response) {
    this.child = response.data;
  }), angular.bind(this, function errorCallback(response) {
    console.log("Error when trying to get child info: " + response);
  }));

  this.http_.get('/manageprogram/getprogram', {
    params:
        {'id': enrollment.program_key.Program}
  }).then(angular.bind(this, function successCallback(response) {
    this.program = JSON.parse(response.data[0]);
  }), angular.bind(this, function() {}));

  this.http_.get('/enrollment/listStatuses').then(angular.bind(this, function successCallback(response) {
    this.allEnrollmentStatuses = response.data;
  }), angular.bind(this, function(){}))
};

EnrollmentEditorController.prototype.getPossibleStatus = function() {
    var enrollment_status = this.enrollment.status;
    if (enrollment_status === 'initialized') {
        return ['cancel', enrollment_status];
    } else if (enrollment_status === 'cancel') {
        return ['initialized', enrollment_status];
    } else {
        return [enrollment_status];
    }
}

EnrollmentEditorController.prototype.cancelEnrollment = function() {

    if (!(this.enrollment.end_date == this.billing_end_date)) {
        console.log("Invalid End Date check");
        this.showWarning = true;
        return ;
    }
    var enrollment_id = this.enrollment.id;
    this.http_.post('/enrollment/cancelEnrollment', {'enrollment_id' : enrollment_id})
    .then(angular.bind(this, function successCallback(response) {
        console.log(response.data);
        this.closeModal(true);
    }), angular.bind(this, function errorCallback(response) {
        console.log(response);
    }));
}

EnrollmentEditorController.prototype.reactivateEnrollment = function() {
    var enrollment_id = this.enrollment.id;
    if (!(this.enrollment.end_date == this.billing_end_date)) {
        console.log("Invalid End Date check");
        this.showWarning = true;
        return ;
    }
    this.http_.post('/enrollment/reactivateEnrollment', {'enrollment_id' : enrollment_id})
    .then(angular.bind(this, function successCallback(response) {
        console.log(response.data);
        this.closeModal(true);
    }), angular.bind(this, function errorCallback(response) {
        console.log(response);
    }));
}

EnrollmentEditorController.prototype.isEnrollmentActive = function() {
    return (this.enrollment.status == 'initialized'
        || this.enrollment.status == 'invited'
        || this.enrollment.status == 'active');
}

EnrollmentEditorController.prototype.$onInit = function() {
    this.renderEnrollmentEditor(this.enrollment);
    this.startDatePickerOpened = false;
};

EnrollmentEditorController.prototype.openStartDatePicker = function() {
  this.startDatePickerOpened = true;
};

EnrollmentEditorController.prototype.openEndDatePicker = function() {
  this.endDatePickerOpened = true;
};

EnrollmentEditorController.prototype.closeModal = function(refresh) {
  this.uibModalInstance_.close({'refresh' : refresh});
}

EnrollmentEditorController.prototype.changeStep = function(step) {
    if (step == 1) {
        this.newEnrollment.start_date_str = moment(this.newEnrollment.start_date).format('LL');
        this.newEnrollment.end_date_str = moment(this.newEnrollment.end_date).format('LL');
    }
    this.currentStep = step;
}


// Disable invalid choices for billing end date
EnrollmentEditorController.prototype.enrollmentDisabledEndDate = function(dateAndMode) {
    return this.enrollmentDateChecker_.isEnrollmentEndDateDisabled(dateAndMode, this.program, this.newEnrollment.start_date);
}

// Disable invalid choices for billing start date
EnrollmentEditorController.prototype.enrollmentDisabledDate = function(dateAndMode) {
    return this.enrollmentDateChecker_.isEnrollmentDateDisabled(dateAndMode, this.program);
}

EnrollmentEditorController.prototype.isStartDateReadOnly = function() {
    var date = this.enrollment.start_date
    var enrollment = this.enrollment;

    var startDate = moment([date.getFullYear(), date.getMonth(), date.getDate()]);
    var currentDate = moment();
    if (startDate <= currentDate) {
        if (enrollment.status === 'active') {
            return true;
        }
    }
    return false;
}

EnrollmentEditorController.prototype.hasChange = function() {
    if (this.enrollment.status !== this.newEnrollment.status) {
        return true;
    }

    if (this.enrollment.start_date.toString() !== this.newEnrollment.start_date.toString()) {
        return true;
    }

    if (this.enrollment.end_date.toString() != this.newEnrollment.end_date.toString()) {
        return true;
    }
    return false;
}


EnrollmentEditorController.prototype.save = function() {
    request = {}
    request.id = this.newEnrollment.id;
    if (this.enrollment.status !== this.newEnrollment.status) {
        request.status = this.newEnrollment.status;
    }
    if (this.enrollment.start_date.toString() !== this.newEnrollment.start_date.toString()) {
        request.start_date = moment(this.newEnrollment.start_date).format("MM/DD/YYYY");
    }
    if (this.enrollment.end_date.toString() != this.newEnrollment.end_date.toString()) {
        request.end_date = moment(this.newEnrollment.end_date).format("MM/DD/YYYY");
    }
    this.http_.post('/enrollment/update', request)
    .then(angular.bind(this, function successCallback(response) {
        this.closeModal(true);
    }),
    angular.bind(this, function errorCallback(response) {} ));
}