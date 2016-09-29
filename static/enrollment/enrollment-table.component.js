angular.
module('enrollmentApp').
component('enrollmentTable', {
    templateUrl: '/static/enrollment/enrollment-table.template.html',
    controller: function EnrollmentTableController($http) {
        console.log('EnrollmentTableController running');
        this.headers = [
            'Child First Name',
            'Child Last Name',
            'Parent First Name',
            'Parent Last Name',
            'Program',
            'Email',
            'Status'];
        $http({
          method: 'GET',
          url: '/enrollment/list'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            console.log(response);
            this.enrollments = [];
            angular.forEach(response.data, angular.bind(this, function(enrollment) {
                this.enrollments.push(JSON.parse(enrollment));
            }));
            console.log(this.enrollments);

          }), function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response);
        });
    }
});
