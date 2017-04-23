ChildFormContentController = function ChildFormContentController($http) {
    this.http_ = $http;
    this.dateOfBirthPickerOpened = false;
    this.startDatePickerOpened = false;
    this.readOnly = false;
    this.todayDate = new Date();
    this.dateFormat = 'MM/DD/YYYY';
    this.showSaveButton = true;
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