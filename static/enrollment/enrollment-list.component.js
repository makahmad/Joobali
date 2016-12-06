EnrollmentListController = function EnrollmentListController($http, $routeParams, $location) {
    var self = this;
    console.log(self.enrollments);
    self.headers = [
        'Program Id',
        'Status',
        'Start Date'
    ];
}