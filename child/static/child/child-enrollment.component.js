ChildEnrollmentController = function ChildEnrollmentController($log, $uibModalInstance, $http, enrollmentDateChecker, child, programs) {
    /*
     * @input: child
     * @input: programs
     */
    var self = this;
    self.child = child;
    self.programs = programs;
    self.currentStep = 0;
    self.newEnrollment = {};
    self.newEnrollment.error = {};
    self.nextButton = {};
    self.saveButton = {};
    self.saveButton.show = true;
    self.doneButton = {};
    self.enrollmentStatus = '';
    this.dateFormat = 'MM/DD/YYYY';
    this.log_ = $log;
    this.enrollmentDateChecker = enrollmentDateChecker;
    this.readOnly = false;
    console.log("Initializing ChildEnrollmentController");


    this.enrollmentDatePickerOptions = {
        minDate: this.todayDate,
        dateDisabled: angular.bind(this, this.enrollmentDisabledDate)
    }

    this.enrollmentEndDatePickerOptions = {
        minDate: this.todayDate,
        dateDisabled: angular.bind(this, this.enrollmentDisabledEndDate)
    }

    self.saveButton.click = function() {

        isValid = true;
        angular.forEach(addEnrollmentForm, function(value, key) {
            if (value.tagName == 'INPUT' || value.tagName == 'SELECT'){
                if(angular.element(value).hasClass('ng-invalid')) {
                    self.newEnrollment.error[value.id] = true;
                    isValid = false;
                } else {
                    self.newEnrollment.error[value.id] = false;
                }
            }
        });
        if (!isValid) {
            return;
        }

        var submittingForm = {
            'child_id': self.child.id,
            'parent_email': self.child.parent_email,
            'program_id': self.newEnrollment.program.id,
            'start_date': moment(self.newEnrollment.start_date).format('MM/DD/YYYY'),
            'end_date' : self.newEnrollment.end_date ? moment(self.newEnrollment.end_date).format('MM/DD/YYYY') : "",
            'waive_registration': self.newEnrollment.waive_registration
        };

        $http.post('/enrollment/add', submittingForm).then(function successCallback(response) {
            var isSaveSuccess = false;
            if (response.data.status == 'success') {
                isSaveSuccess = true;
            }
            if (isSaveSuccess) {
                self.readOnly = true;
                self.enrollmentStatus = 'success';
                self.saveButton.show = false;
                self.doneButton.show = true;
            } else {
                self.enrollmentStatus = 'failure';
                self.failMessage = response.data.message;
            }
        }, function errorCallback(response) {
            self.enrollmentStatus = 'failure';
        });
    }

    self.doneButton.click = function() {
        console.log("doneButton is clicked");
        self.closeModal();
    }

    self.resetButton = function() {
        self.saveButton.show = true;
        self.doneButton.show = false;
    };

    self.resetModal = function() {
        self.todayDate = new Date();
        self.resetButton();
        self.currentStep = 0;
        self.enrollmentStatus = '';
    }

    self.$onInit = function() {
        console.log("self.child: " + JSON.stringify(self.child));
        self.resetModal();
    };

    self.closeModal = function() {
        $uibModalInstance.close();
    }
}

ChildEnrollmentController.prototype.whenSelectedProgramChange = function () {
    this.log_.info("selected program: " + angular.toJson(this.newEnrollment.program));
    if (this.newEnrollment.program) {
        this.log_.info("computing: " + moment(this.newEnrollment.program.startDate));
        this.newEnrollment.start_date = moment(this.newEnrollment.program.startDate).toDate();
    } else {
        this.newEnrollment.start_date = "";
    }
    this.log_.info("setting the start date to be: " + angular.toJson(this.newEnrollment.start_date));
    this.whenChangeStartDate();
}

ChildEnrollmentController.prototype.whenChangeStartDate = function() {
    if (this.newEnrollment.program && this.newEnrollment.program.endDate) {
        this.newEnrollment.end_date = moment(this.newEnrollment.program.endDate).toDate();
    } else {
        this.newEnrollment.end_date = "";
    }
    this.log_.info("setting the end date to be: " + angular.toJson(this.newEnrollment.end_date));
}

ChildEnrollmentController.prototype.getMinEndDate = function() {
    var minDate = null;
    if (this.newEnrollment.start_date) {
        minDate = moment(this.newEnrollment.start_date).add(1, 'day');
    } else {
        minDate = this.todayDate;
    }
    console.log(minDate);
    return minDate;
}

ChildEnrollmentController.prototype.openStartDatePicker = function() {
        this.startDatePickerOpened = true;
}

ChildEnrollmentController.prototype.openEndDatePicker = function() {
        this.endDatePickerOpened = true;
}

// Disable invalid choices for billing end date
ChildEnrollmentController.prototype.enrollmentDisabledEndDate = function(dateAndMode) {
    return this.enrollmentDateChecker.isEnrollmentEndDateDisabled(
            dateAndMode,
            this.newEnrollment.program,
            this.newEnrollment.start_date);
}

// Disable invalid choices for billing start date
ChildEnrollmentController.prototype.enrollmentDisabledDate = function(dateAndMode) {
    return this.enrollmentDateChecker.isEnrollmentDateDisabled(
        dateAndMode,
        this.newEnrollment.program);
}
