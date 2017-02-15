EnrollmentListController = function EnrollmentListController($uibModal, $log, $http) {
    var self = this;
    console.log(self.enrollments);
    console.log(self.child);
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
