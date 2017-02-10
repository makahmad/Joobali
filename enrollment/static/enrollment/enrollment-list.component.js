EnrollmentListController = function EnrollmentListController($uibModal) {
    var self = this;
    console.log(self.enrollments);
    self.headers = [
        'Program Id',
        'Status',
        'Start Date',
        ''
    ];

    self.openEnrollmentEditorModal = function(enrollment) {
        console.log("Opening Add Enrollment Modal");
        console.log("Enrollment is " + JSON.stringify(enrollment));
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: '/static/enrollment/enrollment-editor.template.html',
            controller: 'EnrollmentEditorController',
            controllerAs: '$ctrl',
            resolve: {
                enrollment: function() {
                    return enrollment;
                },
            }
        });
    };
}
