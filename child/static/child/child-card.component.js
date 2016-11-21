ChildCardController = function ChildCardController($scope, $http, $routeParams, $location) {

    this.getProgramData = function() {
        $http({
            method: 'GET',
            url: '/manageprogram/listprograms'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            this.programs = [];
            angular.forEach(response.data, angular.bind(this, function(program) {
                this.programs.push(JSON.parse(program));
            }));
        }), function errorCallback(response) {
            // TODO(zilong): deal with error here
        });
    };

    this.addEnrollmentHandleSave = function() {
        console.log("Save Enrollment");
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
        console.log("child is " + this.child);
        console.log("index is " + this.index);
        this.initializeTimePickers();
        this.getProgramData();
        this.resetModal();
    };
}


ChildCardController.prototype.initializeTimePickers = function() {
    $('#startDate').datetimepicker({
        format: 'MM/DD/YYYY',
        // Assuming all enrollment has start date later or equal than today
        minDate: new Date(),
    });
}