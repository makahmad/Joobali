ChildEnrollmentController = function ChildEnrollmentController($http, $routeParams, $location) {

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
        console
        $("#addEnrollmentNextButton-" + this.cardIndex).show();
        $("#addEnrollmentSaveButton-" + this.cardIndex).hide();
        $("#addEnrollmentDoneButton-" + this.cardIndex).hide();
    };

    this.$onInit = function() {
        console.log("cardIndex is " + this.cardIndex);
        this.getProgramData();
        this.resetButton()
    };
}