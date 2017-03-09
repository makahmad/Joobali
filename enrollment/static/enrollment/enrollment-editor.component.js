EnrollmentEditorController = function EnrollmentEditorController($uibModalInstance, $http, enrollment) {
    var self = this;
    self.enrollment = enrollment;
    self.startDatePickerOpened = false;
    self.child = {};
    // Functions
    self.renderEnrollmentEditor = function(enrollment) {
      var child_key = enrollment.child_key;
      var child_id = child_key.Child;
      var get_child_request = {'child_id' : child_id};
      $http.post('/child/get', get_child_request)
      .then(function successCallback(response) {
        self.child = response.data;
        console.log(self.child)
      }, function errorCallback(response) {
        console.log("Error when trying to get child info: " + response);
      });
      var get_program_request = {'program_id': enrollment.program_key.Program};
    };

    self.cancelEnrollment = function() {
        var enrollment_id = enrollment.id;
        $http.post('/enrollment/cancelEnrollment', {'enrollment_id' : enrollment_id})
        .then(function successCallback(response) {
            console.log(response.data);
            self.closeModal(true);
        }, function errorCallback(response) {
            console.log(response);
        });
    }

    self.reactivateEnrollment = function() {
        var enrollment_id = enrollment.id;
        $http.post('/enrollment/reactivateEnrollment', {'enrollment_id' : enrollment_id})
        .then(function successCallback(response) {
            console.log(response.data);
            self.closeModal(true);
        }, function errorCallback(response) {
            console.log(response);
        });
    }

    self.isEnrollmentActive = function() {
        return (self.enrollment.status == 'initialized'
            || self.enrollment.status == 'invited'
            || self.enrollment.status == 'active');
    }

    self.$onInit = function() {
        self.renderEnrollmentEditor(self.enrollment);
        self.startDatePickerOpened = false;
    };

    self.openStartDatePicker = function() {
      self.startDatePickerOpened = true;
    };

    self.closeModal = function(refresh) {
      $uibModalInstance.close({'refresh' : refresh});
    }
}
