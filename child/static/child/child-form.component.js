ChildFormController = function ChildFormController($http, $routeParams, $location) {
    var self = this;

    self.dateOfBirthFormat = 'MM/dd/yyyy';
    self.dateOfBirthPickerOpened = false;
    self.childInfo = {};
    self.currentStep = 0;

    self.nextButton = {};
    self.saveButton = {};
    self.doneButton = {};
    self.saveSuccessLabel = {};
    self.saveFailLabel = {};

    self.doneButton.click = function() {
        console.log("resetting Modal");
        self.resetModal();
    };

    self.saveButton.click = function() {
        console.log("save");
        console.log(self.childInfo);
        var submittingForm = angular.copy(self.childOverview);
        console.log("submitting " + submittingForm);
        $http.post('/child/add', submittingForm).then(function successCallback(response) {
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
    };

    self.nextButton.click = function() {
        var isValid = true;
        angular.forEach(addChildForm, function(value, key) {
            if(value.validity.valid != true) {
                isValid = false;
            }
        })

        self.currentStep += 1;
        if (isValid) {
            if (self.currentStep == 1) {
                console.log("childInfo: " + self.childInfo);
                self.childOverview = angular.copy(self.childInfo);
                self.childOverview.date_of_birth = moment(self.childOverview.date_of_birth).format('MM/DD/YYYY');
                console.log("Reach the final step");
                self.nextButton.show = false;
                self.saveButton.show = true;
            } else {
                self.resetButton();
            }
        }
    };

    self.resetButton = function() {
        self.nextButton.show = true;
        self.saveButton.show = false;
        self.doneButton.show = false;
    };

    self.resetModal = function() {
        self.childInfo = {};
        self.childOverview = {};
        self.currentStep = 0;
        self.saveSuccessLabel.show = false;
        self.saveFailLabel.show = false;
        self.resetButton();
    }

    self.openDateOfBirthPicker = function() {
        console.log("Toggle Date picker: " + self.dateOfBirthPickerOpened);
        self.dateOfBirthPickerOpened = ! self.dateOfBirthPickerOpened;
    }

    self.$onInit = function() {
        self.dateOfBirthPickerOpened = false;
        self.resetButton();
        self.currentStep = 0;
    }
}
