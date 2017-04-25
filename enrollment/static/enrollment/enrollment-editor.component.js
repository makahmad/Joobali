EnrollmentEditorController = function EnrollmentEditorController($uibModalInstance, $http, enrollment) {
    this.uibModalInstance_ = $uibModalInstance;
    this.http_ = $http;

    this.enrollment = enrollment;
    this.startDatePickerOpened = false;
    this.child = {};
    this.program = {};
    // Functions
}

EnrollmentEditorController.prototype.renderEnrollmentEditor = function(enrollment) {
  var child_key = enrollment.child_key;
  var child_id = child_key.Child;
  var get_child_request = {'child_id' : child_id};
  this.http_.post('/child/get', get_child_request)
  .then(angular.bind(this, function successCallback(response) {
    this.child = response.data;
    console.log(this.child)
  }), angular.bind(this, function errorCallback(response) {
    console.log("Error when trying to get child info: " + response);
  }));

  this.http_.get('/manageprogram/getprogram', {
    params:
        {'id': enrollment.program_key.Program}
  }).then(angular.bind(this, function successCallback(response) {
    console.log(response);
    console.log(response.data);
    console.log(response.data[0]);
    console.log(JSON.parse(response.data[0]).programName);
    this.program = JSON.parse(response.data[0]);
  }), angular.bind(this, function() {}));
};

EnrollmentEditorController.prototype.cancelEnrollment = function() {
    console.log(this.enrollment.start_date);
    console.log(this.billing_start_date);
    if (!(this.enrollment.start_date == this.billing_start_date)) {
        console.log("Invalid Start Date check");
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
    if (!(this.enrollment.start_date == this.billing_start_date)) {
        console.log("Invalid Start Date check");
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

EnrollmentEditorController.prototype.closeModal = function(refresh) {
  this.uibModalInstance_.close({'refresh' : refresh});
}
