enrollmentFormController = function EnrollmentFormController($http, $location) {
    console.log('EnrollmentFormController running');
    this.enrollmentInfo = {};

    this.headers = [
        'Child First Name',
        'Child Last Name',
        'Parent First Name',
        'Parent Last Name',
        'Email',
        'Program Id',
        'Status'
    ];

    this.getProgramData = function() {
        $http({
            method: 'GET',
            url: '/manageprogram/listprograms'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            console.log(response);
            this.programs = [];
            angular.forEach(response.data, angular.bind(this, function(program) {
                this.programs.push(JSON.parse(program));
            }));
            console.log(this.programs)
        }), function errorCallback(response) {
            // TODO(zilong): deal with error here
        });
    }

    this.refreshEnrollment = function() {
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
            // TODO(zilong): deal with error here
            console.log(response);
        });
    };

    this.handleDone = function() {
        this.enrollmentInfo = {};
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
        this.refreshEnrollment();
    };

    this.handleSave = function() {
        console.log("save");
        console.log(this.enrollmentInfo);
        var submittingForm = angular.copy(this.enrollmentInfo);
        console.log(submittingForm);
        submittingForm.program_id = submittingForm.program.id;
        delete submittingForm['program'];
        console.log("submitting " + submittingForm);
        $http.post('/enrollment/add', submittingForm).then(function successCallback(response) {
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

    this.handleNext = function() {
        console.log($(".enrollment-form-content.active"));
        var curContent = $(".enrollment-form-content.active");
        var curNav = $(".form-nav.active");

        var curInputs = curContent.find("input");
        isValid = true;
        $(".form-group").removeClass("has-error");
        for (var i = 0; i < curInputs.length; i++) {
            console.log(curInputs[i].validity.valid);
            if (!curInputs[i].validity.valid) {
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
                $("#step2").removeClass("hide");
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

    this.editView = function(enrollmentId, programId) {
        console.log("enrollmentId: " + enrollmentId + ", programId: " + programId);
        $location.path("/enrollment/edit/" + enrollmentId + "/" + programId);
        console.log($location.path());
    }

    this.$onInit = function() {
        this.refreshEnrollment();
        this.getProgramData();
    }
}