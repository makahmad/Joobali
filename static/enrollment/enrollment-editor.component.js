angular
.module('enrollmentApp')
.component('enrollmentEditor', {
    templateUrl: '/static/enrollment/enrollment-editor.template.html',
    controller : ['$http', '$routeParams', '$location',
        function EnrollmentEditorController($http, $routeParams, $location) {

            // Fields
            this.enrollmentId = $routeParams.enrollmentId;
            this.programId = $routeParams.programId;
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
                    // TODO(zilong): deal with error here
                    console.log(response);
                });
            };

            this.handleSave = function() {
                console.log("save");
                console.log(this.enrollmentInfo);
                var submittingFormEnrolmentInfo = angular.copy(this.enrollmentInfo);
                console.log(submittingFormEnrolmentInfo);
                submittingFormEnrolmentInfo.program_id = this.programId;
                delete submittingFormEnrolmentInfo['program'];
                console.log("submitting " + submittingFormEnrolmentInfo);
                $http.post('/enrollment/update', submittingFormEnrolmentInfo).then(function successCallback(response) {
                    var isSaveSuccess = false;
                    console.log(response);
                    if (response.data.status == 'success') {
                        isSaveSuccess = true;
                    }
                    if (isSaveSuccess) {
                        $("#saveSuccessLabel").removeClass('hide');
                        $("#saveFailureLabel").addClass('hide');
                        $("#saveButton").hide();
                        $("#doneButton").show();
                    } else {
                        $("#saveSuccessLabel").addClass('hide');
                        $("#saveFailureLabel").removeClass('hide');
                    }
                }, function errorCallback(response) {
                    $("#saveSuccessLabel").addClass('hide');
                    $("#saveFailureLabel").removeClass('hide');
                });
            };

            this.switchToEnrollmentHome = function() {
                $location.path("");
            }

            this.$onInit = function() {
                this.renderEnrollmentEditor(this.enrollmentId, this.programId);
            };
        }
    ]
});