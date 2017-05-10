EnrollmentListController = function EnrollmentListController($uibModal, $log, $http) {
    this.uibModal_ = $uibModal;
    var self = this;
    self.headers = [
        'Program Name',
        'Status',
        'Start Date',
        'Billing Frequency'
    ];

    self.openEnrollmentEditorModal = function(enrollment) {

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

        modalInstance.result.then(function (data) {
            $log.info(data);
            if (data.refresh == true) {
                self.refreshEnrollment();
            }
        }, function () {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    self.refreshEnrollment = function() {
        $http.post('/enrollment/listByChildId', { 'child_id' : self.child.id })
        .then(angular.bind(this, function successCallback(response) {
            this.enrollments = [];
            console.log('enrollment/listByChild: ' + response.data)
            angular.forEach(response.data, angular.bind(this, function(enrollment) {
                this.enrollments.push(JSON.parse(enrollment));
            }));
        }), angular.bind(this, function errorCallback(response){
        }));
    }
}

EnrollmentListController.prototype.openEnrollmentResendInvitationModal = function(enrollment) {
    var modalInstance = this.uibModal_.open({
        animation: true,
        templateUrl: '/static/enrollment/enrollment-resend-invitation-dialog.template.html',
        controller: 'EnrollmentResendInvitationDialogController',
        controllerAs: '$ctrl',
        resolve: {
            enrollment: function() {
                return enrollment;
            },
        }
    });

    modalInstance.result.then(function (data) {
        $log.info(data);
        if (data.refresh == true) {
            self.refreshEnrollment();
        }
    }, function () {
        $log.info('Modal dismissed at: ' + new Date());
    });
}

EnrollmentListController.prototype.canResendEnrollmentInvitation = function(enrollment) {
    return (enrollment.status == 'initialized' || enrollment.status == 'invited')
}