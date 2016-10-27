angular
.module('enrollmentApp')
.component('enrollmentEditor', {
    templateUrl: '/static/enrollment/enrollment-editor.template.html',
    controller : ['$http', '$routeParams',
        function EnrollmentEditorController($http, $routeParams) {
            // Fields
            var enrollmentKey = $routeParams.enrollmentKey;
            var tokens = enrollmentKey.split("-");
            this.enrollmentId = tokens[0];
            this.programId = tokens[1];
            this.enrollmentInfo = {};

            // Functions

            this.renderEnrollmentEditor = function(enrollmentId, programId) {
                $http({
                    method: 'GET',
                    url: '/enrollment/get?enrollmentId=' + enrollmentId + '&programId=' + programId
                }).then(angular.bind(this, function successCallback(response) {
                    // this callback will be called asynchronously
                    // when the response is available
                    this.enrollmentInfo = angular.fromJson(angular.fromJson(response.data));
                    console.log(response.data);
                    console.log(this.enrollmentInfo);
                    console.log(typeof(this.enrollmentInfo));
                    console.log(this.enrollmentInfo.parent_first_name);
                }), function errorCallback(response) {
                    // TODO(zilong): deal with erro here
                    console.log(response);
                });
            };

            this.$onInit = function() {
                this.renderEnrollmentEditor(this.enrollmentId, this.programId);
            };
        }
    ]
});