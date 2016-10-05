angular.
module('enrollmentApp').
component('enrollment', {
    templateUrl: '/static/enrollment/enrollment.template.html',
    controller: ['$http',
        function EnrollmentFormController($http) {
            console.log('EnrollmentFormController running');
            this.form = {};

            this.headers = [
            'Child First Name',
            'Child Last Name',
            'Parent First Name',
            'Parent Last Name',
            'Program',
            'Email',
            'Status'];

            this.refreshData = function() {
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
            };

            this.handleDone = function() {
                this.form = {};
                $("#addEnrollmentModal").modal('hide');
                console.log($(".form-content.active"));
                var curContent = $(".form-content.active");
                var curNav = $(".form-nav.active");
                curNav.removeClass("active");
                curContent.removeClass("active").hide();

                var formStep1 = $("#step1");
                var navStep1 = $("#navStep1");
                navStep1.addClass("active");
                formStep1.addClass("active").show();
                this.resetButton();
                this.resetSaveResult();
                this.refreshData();
            };

            this.handleSave = function() {
                console.log("save");
                console.log(this.form);
                $http.post('/enrollment/add', this.form).then(function successCallback(response) {
                    // TODO(zilong): Judge whether the save is success
                    var isSaveSuccess = true;
                    if (isSaveSuccess) {
                        $("#saveSuccessLabel").removeClass('hide');
                        $("#saveFailureLabel").addClass('hide');
                    } else {
                        $("#saveSuccessLabel").addClass('hide');
                        $("#saveFailureLabel").removeClass('hide');
                    }
                    $("#doneButton").show();
                }, function errorCallback(response) {
                    $("#saveSuccessLabel").addClass('hide');
                    $("#saveFailureLabel").removeClass('hide');
                });
            };

            this.handleNext = function() {
                console.log($(".form-content.active"));
                var curContent = $(".form-content.active");
                var curNav = $(".form-nav.active");

                var curInputs = curContent.find("input");
                isValid = true;
                $(".form-group").removeClass("has-error");
                for(var i=0; i< curInputs.length; i++){
                    console.log(curInputs[i].validity.valid);
                    if (!curInputs[i].validity.valid){
                        isValid = false;
                        $(curInputs[i]).closest(".form-group").addClass("has-error");
                    }
                }
                console.log(isValid);

                if (isValid) {
                    curNav.removeClass("active");
                    curNav.next().addClass("active");
                    curContent.removeClass("active").hide();
                    curContent.next().addClass("active").show();

                    if (curNav.next().attr('id') === "navStep2") {
                        $("#nextButton").hide();
                        $("#saveButton").show();
                    } else {
                        console.log(this.resetButton);
                        this.resetButton();
                    }
                }
            };

            this.resetButton = function() {
                $("#nextButton").show();
                $("#saveButton").hide();
                $("#doneButton").hide();
            };

            this.resetSaveResult = function() {
                $("#saveSuccessLabel").addClass('hide');
                $("#saveFailureLabel").addClass('hide');
            }

            this.$onInit = function() {
                this.refreshData();
            }
        }
    ]
});
