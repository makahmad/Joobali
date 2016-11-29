ChildEnrollmentController = function ChildEnrollmentController() {
    /*
     * @input: child
     * @input: programs
     *
     */

    this.newEnrollment = {};
    this.addEnrollmentHandleSave = function() {
        console.log("Save Enrollment");
        console.log("enrollment info " + JSON.stringify(this.newEnrollment));
        console.log("$ctrl.startDate:" + this.startDate);
    }

    this.addEnrollmentHandleNext = function() {
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
                this.showStep2 = true;
                this.showNextButton = false;
                this.showSaveButton = true;
            } else {
                console.log(this.resetButton);
                this.resetButton();
            }
        }
    };

    this.openStartDatePicker = function() {
        this.startDatePickerOpened = true;
    }

    this.resetButton = function() {
        this.showNextButton = true;
        this.showSaveButton = false;
        this.showDoneButton = false;
    };

    this.resetModal = function() {
        this.showStep2 = false;
        this.resetButton();
    }

    this.$onInit = function() {
        this.resetModal();
    };
}