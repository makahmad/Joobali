ChildEnrollmentController = function ChildEnrollmentController($uibModalInstance, $http, child, programs) {
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

    this.days = {
        'Sunday': 0,
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6
    }

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
        self.newEnrollment.child_id = self.child.id;
        self.newEnrollment.start_date = moment(self.newEnrollment.start_date).format('MM/DD/YYYY');
        self.newEnrollment.end_date = self.newEnrollment.end_date ? moment(self.newEnrollment.end_date).format('MM/DD/YYYY') : "";
        var submittingForm = {
            'child_id': self.child.id,
            'parent_email': self.child.parent_email,
            'program_id': self.newEnrollment.program.id,
            'start_date': self.newEnrollment.start_date,
            'end_date' : self.newEnrollment.end_date ? self.newEnrollment.end_date : "",
            'waive_registration': self.newEnrollment.waive_registration
        };
        console.log(submittingForm);
        $http.post('/enrollment/add', submittingForm).then(function successCallback(response) {
            var isSaveSuccess = false;
            console.log(response);
            if (response.data.status == 'success') {
                isSaveSuccess = true;
            }
            if (isSaveSuccess) {
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
    if (this.newEnrollment.program) {
        this.newEnrollment.start_date = moment(this.newEnrollment.program.startDate, this.dateFormat).toDate();
        if (this.newEnrollment.program.endDate) {
            this.newEnrollment.end_date = moment(this.newEnrollment.program.endDate, this.dateFormat).toDate();
            this.newEnrollment.no_end_date = false;
        } else {
            this.newEnrollment.no_end_date = true;
        }
    } else {
        this.newEnrollment.start_date = null;
    }
    this.whenChangeStartDate();
}

ChildEnrollmentController.prototype.whenChangeStartDate = function(isManualChange) {
    if (isManualChange) {
        this.newEnrollment.no_end_date = false;
    }
    this.whenChangeNoEndDate();
}

ChildEnrollmentController.prototype.whenChangeNoEndDate = function() {
    if (this.newEnrollment.no_end_date) {
        this.newEnrollment.end_date = null;
    }
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
    if (dateAndMode.mode === 'day') {
        if (this.newEnrollment.start_date) {
            var currentDate = moment([dateAndMode.date.getFullYear(), dateAndMode.date.getMonth(), dateAndMode.date.getDate()]);
            if (currentDate <= this.newEnrollment.start_date) {
                return true;
            }
        }

        if (this.newEnrollment.program) {
            if (this.newEnrollment.program.endDate) {
                if (this.newEnrollment.program.monthlyBillDay === 'Last Day') {
                    if (currentDate.date() != currentDate.daysInMonth()) {
                        return true;
                    }
                } else {
                    var programEndDate = moment(this.newEnrollment.program.endDate, this.dateFormat);
                    if (currentDate > programEndDate) {
                        return true;
                    }
                }
            }
        }
    }
    return this.enrollmentDisabledDate(dateAndMode);
}

// Disable invalid choices for billing start date
ChildEnrollmentController.prototype.enrollmentDisabledDate = function(dateAndMode) {
    var result = false;
    if (dateAndMode.mode === 'day') {
        var today = moment(new Date());
        var currentDate = moment([dateAndMode.date.getFullYear(), dateAndMode.date.getMonth(), dateAndMode.date.getDate()]);
        if (currentDate.diff(today, 'days') < 5) {
            return true;
        }

        if (this.newEnrollment != null &&
                this.newEnrollment.program != null &&
                this.newEnrollment.program.billingFrequency != null) {
            if (this.newEnrollment.program.billingFrequency === 'Weekly') {
                result =  (dateAndMode.date.getDay() != this.days[this.newEnrollment.program.weeklyBillDay]);
            } else if (this.newEnrollment.program.billingFrequency === 'Monthly') {
                if (this.newEnrollment.program.monthlyBillDay === 'Last Day') {
                    result = (dateAndMode.date.getDate() != currentDate.daysInMonth());
                } else {
                    result = (dateAndMode.date.getDate() != this.newChildEnrollmentInfo.program.monthlyBillDay);
                }
            }
        }

        if (this.newEnrollment.program) {
            var programStartDate = moment(this.newEnrollment.program.startDate, this.dateFormat);
            if (currentDate < programStartDate) {
                return true;
            }
        }
    }
    return result;
}
