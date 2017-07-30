EnrollmentEditorController = function EnrollmentEditorController($uibModalInstance, $http, EnrollmentDateChecker, enrollment) {
    this.uibModalInstance_ = $uibModalInstance;
    this.http_ = $http;
    this.enrollmentDateChecker_ = EnrollmentDateChecker;

    this.enrollment = enrollment;
    this.enrollment.start_date = moment(enrollment.start_date).toDate();
    this.enrollment.start_date_str = moment(enrollment.start_date).format("LL");

    if (enrollment.end_date) {
        this.enrollment.end_date_str = moment(enrollment.end_date).format("LL");
    } else {
        this.enrollment.end_date_str = "Never ends";
    }

    this.enrollment.end_date = moment(enrollment.end_date).toDate();

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

    this.enrollmentMap = {'initialized':'Invited (but not accepted)', 'cancel':'Cancel','active':'Active','invited':'Invited'};
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
  if( !this.isStartDateReadOnly() )
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

        if(this.newEnrollment.end_date) {
            this.newEnrollment.end_date_str = moment(this.newEnrollment.end_date).format('LL');
        } else {
            this.newEnrollment.end_date_str = "Never ends";
        }
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

    if (enrollment.status === 'active') {
        var startDate = moment([date.getFullYear(), date.getMonth(), date.getDate()]);
        var currentDate = moment();
        var dateDelta = startDate.diff(currentDate, 'days');
        // start date is read-only if the enrollment start date is within 5 days of current date, because invoice may
        // have been generated
        if (dateDelta <= 5) {
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

    if (this.isEndDateChanged()) {
        return true;
    }

    return false;
}

EnrollmentEditorController.prototype.isEndDateChanged = function() {
    if (this.enrollment.end_date == null) {
        if(this.newEnrollment.end_date != null) {
            return true;
        }
    } else {
        if(!this.newEnrollment.end_date) {
            return true;
        }
        if(this.enrollment.end_date.toString() != this.newEnrollment.end_date.toString()) {
            return true;
        }
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
    if (this.isEndDateChanged()) {
        if(this.newEnrollment.end_date) {
            request.end_date = moment(this.newEnrollment.end_date).format("MM/DD/YYYY");
        } else {
            request.end_date = '';
        }
    }
    this.http_.post('/enrollment/update', request)
    .then(angular.bind(this, function successCallback(response) {
        this.closeModal(true);
    }),
    angular.bind(this, function errorCallback(response) {} ));
}