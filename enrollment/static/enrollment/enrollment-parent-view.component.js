EnrollmentParentViewController = function EnrollmentParentViewController($http, $routeParams) {
    var self = this;
    self.enrollmentId = $routeParams.enrollmentId;
    self.providerId = $routeParams.providerId;

    self.$onInit = function() {
        self.enrollmentId = $routeParams.enrollmentId;
        self.providerId = $routeParams.providerId;
    }
}
