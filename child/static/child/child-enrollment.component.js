ChildEnrollmentController = function ChildEnrollmentController($uibModalInstance, $http, child, programs) {
    /*
     * @input: child
     * @input: programs
     */
    var self = this;
    self.child = child;
    self.programs = programs;
    self.currentStep = 0;
    self.newEnrollment = {};
    self.nextButton = {};
    self.saveButton = {};
    self.doneButton = {};
    self.saveSuccessLabel = {};
    self.saveFailLabel = {};

    self.saveButton.click = function() {
        console.log("saveButton is clicked");
        var submittingForm = {
            'child_id': self.child.id,
            'parent_email': self.child.parent_email,
            'program_id': self.newEnrollment.program.id,
            'start_date': self.newEnrollment.start_date
        };
        console.log(submittingForm);
        $http.post('/enrollment/add', submittingForm).then(function successCallback(response) {
            var isSaveSuccess = false;
            console.log(response);
            if (response.data.status == 'success') {
                isSaveSuccess = true;
            }
            if (isSaveSuccess) {
                self.saveSuccessLabel.show = true;
                self.saveFailLabel.show = false;
                self.saveButton.show = false;
                self.doneButton.show = true;
            } else {
                self.saveSuccessLabel.show = false;
                self.saveFailLabel.show = true;
            }
        }, function errorCallback(response) {
            self.saveSuccessLabel.show = false;
            self.saveFailLabel.show = true;
        });
    }

    self.doneButton.click = function() {
        console.log("doneButton is clicked");
        self.closeModal();
    }

    self.nextButton.click = function() {
        var isValid = true;

        console.log(isValid);
        self.currentStep += 1;
        if (isValid) {
            if (self.currentStep == 1) {
                self.newEnrollment.child_id = self.child.id;
                self.newEnrollment.start_date = moment(self.newEnrollment.start_date).format('MM/DD/YYYY');
                console.log("self.newEnrollment.start_date: " + self.newEnrollment.start_date);
                self.nextButton.show = false;
                self.saveButton.show = true;
            } else {
                console.log(this.resetButton);
                self.resetButton();
            }
        }
    };

    self.openStartDatePicker = function() {
        self.startDatePickerOpened = true;
    }

    self.resetButton = function() {
        self.nextButton.show = true;
        self.saveButton.show = false;
        self.doneButton.show = false;
    };

    self.resetModal = function() {
        self.todayDate = new Date();
        self.resetButton();
        self.currentStep = 0;
        self.saveSuccessLabel.show = false;
        self.saveFailLabel.show = false;
    }

    self.$onInit = function() {
        console.log("self.child: " + JSON.stringify(self.child));
        self.resetModal();
    };

    self.closeModal = function() {
        $uibModalInstance.close();
    }
}
