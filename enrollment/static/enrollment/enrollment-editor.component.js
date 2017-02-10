EnrollmentEditorController = function EnrollmentEditorController($uibModalInstance, $http, enrollment) {
    var self = this;
    self.enrollment = enrollment;
    self.startDatePickerOpened = false;
    self.child = {};
    // Functions
    self.renderEnrollmentEditor = function(enrollment) {
      var child_key = enrollment.child_key;
      var child_id = child_key[0][1];
      var get_child_request = {'child_id' : child_id};
      $http.post('/child/get', get_child_request)
      .then(function successCallback(response) {
        self.child = response.data;
        console.log(self.child)
      }, function errorCallback(response) {
        console.log("Error when trying to get child info: " + response);
      });
      var get_program_request = {'program_id': enrollment.program_key[1][1]};
    };

    self.handleSave = function() {
    };

    self.$onInit = function() {
        self.renderEnrollmentEditor(self.enrollment);
        self.startDatePickerOpened = false;
    };

    self.openStartDatePicker = function() {
      self.startDatePickerOpened = true;
    };
    self.closeModal = function() {
      $uibModalInstance.close();
    }
}
