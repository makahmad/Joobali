childFormController = function ChildFormController($http, $routeParams, $location) {
    this.handleDone = function() {
        this.enrollmentInfo = {};
        $("#addChildModal").modal('hide');
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
        console.log(this.childInfo);
        var submittingForm = angular.copy(this.childInfo);
        console.log("submitting " + submittingForm);
        $http.post('/child/add', submittingForm).then(function successCallback(response) {
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
        console.log($(".child-form-content.active"));
        var curContent = $(".child-form-content.active");
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
}