EnrollmentResendInvitationDialogController = function EnrollmentResendInvitationDialogController($uibModalInstance, $http, enrollment) {
    this.uibModalInstance_ = $uibModalInstance;
    this.http_ = $http;
    this.enrollment_ = enrollment;
}


EnrollmentResendInvitationDialogController.prototype.resendEnrollmentInvitation = function() {
    this.http_.post('/enrollment/resendInvitation', this.enrollment_).then(angular.bind(this, function successCallback(response) {
        console.log("new invitation email sent!");
        this.closeModal();
    }), angular.bind(this, function errorCallback(response) {
    }));
}


EnrollmentResendInvitationDialogController.prototype.closeModal = function(refresh) {
  this.uibModalInstance_.close();
}
