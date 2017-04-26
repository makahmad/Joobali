ChildFormContentController = function ChildFormContentController($http) {
    this.http_ = $http;
    this.dateOfBirthPickerOpened = false;
    this.startDatePickerOpened = false;
    this.readOnly = false;
    this.todayDate = new Date();
    this.dateFormat = 'MM/DD/YYYY';
    this.showSaveButton = true;
    this.newChildEnrollmentInfo = {};
    this.enrollmentDatePickerOptions = {
        minDate: this.todayDate,
        dateDisabled: angular.bind(this, this.enrollmentDisabledDate)
    }

    this.days = {
        'Sunday': 0,
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6
    }
}

ChildFormContentController.prototype.enrollmentDisabledDate = function(dateAndMode) {
    var result = false;
    if (dateAndMode.mode === 'day') {
        if (this.newChildEnrollmentInfo != null &&
                this.newChildEnrollmentInfo.program != null &&
                this.newChildEnrollmentInfo.program.billingFrequency != null) {
            if (this.newChildEnrollmentInfo.program.billingFrequency === 'Weekly') {
                result =  (dateAndMode.date.getDay() != this.days[this.newChildEnrollmentInfo.program.weeklyBillDay]);
            } else if (this.newChildEnrollmentInfo.program.billingFrequency === 'Monthly') {
                result = (dateAndMode.date.getDate() != this.newChildEnrollmentInfo.program.monthlyBillDay);
            }
        }
    }
    return result;
}

ChildFormContentController.prototype.openDateOfBirthPicker = function() {
    this.dateOfBirthPickerOpened = ! this.dateOfBirthPickerOpened;
};

ChildFormContentController.prototype.openStartDatePicker = function() {
    this.startDatePickerOpened = ! this.startDatePickerOpened;
};

ChildFormContentController.prototype.save = function() {
    isValid = true;
    angular.forEach(addChildForm, function(value, key) {
        if (value.tagName == 'INPUT' || value.tagName == 'SELECT'){
            if(angular.element(value).hasClass('ng-invalid')) {
                isValid = false;
            }
        }
    });
    if (!isValid) {
        return;
    }

    var submittingForm = angular.copy(this.newChildEnrollmentInfo);
    submittingForm.child_date_of_birth = moment(submittingForm.child_date_of_birth).format("MM/DD/YYYY");
    submittingForm.start_date = moment(submittingForm.start_date).format("MM/DD/YYYY");
    this.http_.post('/child/add', submittingForm).then(angular.bind(this, function successCallback(response) {
        if (response.data.status == 'success') {
            this.showSaveButton = false;
            this.onSave({'isSaved': true});
            this.readOnly = true;
        } else {
            this.onSave({'isSaved': false});
            this.readOnly = false;
        }
    }), angular.bind(this, function errorCallback(response) {
        // TODO(zilong): Handle RESTFul error properly
    }));
}