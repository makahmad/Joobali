ChildFormController = function ChildFormController($http, $routeParams, $location) {

    this.dateOfBirthFormat = 'MM/dd/yyyy';
    this.dateOfBirthPickerOpened = false;
    this.childInfo = {};
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
        // this.refreshEnrollment();
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

    this.handleSave = function() {
        console.log("save");
        console.log(this.childInfo);
        var submittingForm = angular.copy(this.childOverview);
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
                $("#addChildSaveButton").hide();
                $("#addChildDoneButton").show();
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
        var curContent = $(".child-form-content.active");
        var curNav = $(".form-nav.active");

        var curInputs = curContent.find("input");
        isValid = true;
        $(".form-group").removeClass("has-error");
        for (var i = 0; i < curInputs.length; i++) {
            if (!curInputs[i].validity.valid) {
                isValid = false;
                $(curInputs[i]).closest(".form-group").addClass("has-error");
            }
        }
        console.log("Input validity is " + isValid);

        if (isValid) {
            curNav.removeClass("active");
            curNav.next().addClass("active");
            console.log("curContent " + curContent.attr('class').split(/\s+/));
            curContent.removeClass("active").hide();
            // curContent.next().removeClass("hide");
            curContent.next().addClass("active").show();

            if (curNav.next().attr('id') == "navStep2") {
                this.childOverview = angular.copy(this.childInfo);
                this.childOverview.date_of_birth = moment(this.childOverview.date_of_birth).format('MM/DD/YYYY');
                console.log("Reach the final step");
                $("#addChildstep2").removeClass("hide");
                $("#addChildNextButton").hide();
                $("#addChildSaveButton").show();
            } else {
                console.log(this.resetButton);
                this.resetButton();
            }
        }
    };

    this.openDateOfBirthPicker = function() {
        console.log("Toggle Date picker: " + this.dateOfBirthPickerOpened);
        this.dateOfBirthPickerOpened = ! this.dateOfBirthPickerOpened;
    }

    this.$onInit = function() {
        this.dateOfBirthPickerOpened = false;
        this.initializeTimePickers();
    }
}

ChildFormController.prototype.initializeTimePickers = function() {
    /*
    $('#dateOfBirth').datetimepicker({
        format: 'MM/DD/YYYY',
        minDate: new Date("01/01/1970"),
        maxDate: new Date()
    });
    */
}
