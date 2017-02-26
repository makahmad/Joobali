ChildFormController = function ChildFormController($uibModalInstance, $http) {
    var self = this;

    self.dateOfBirthFormat = 'MM/dd/yyyy';
    self.dateOfBirthPickerOpened = false;
    self.childInfo = {};
    self.programs = {};
    self.currentStep = 0;

    self.nextButton = {};
    self.saveButton = {};
    self.doneButton = {};
    self.saveSuccessLabel = {};
    self.saveFailLabel = {};

    self.doneButton.click = function() {
        self.resetModal();
        self.closeModal();
    };

    self.saveButton.click = function() {
        var submittingForm = angular.copy(self.overview);
        $http.post('/child/add', submittingForm).then(function successCallback(response) {
            var isSaveSuccess = false;
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
            if (self.currentStep == 2) {
                self.overview = angular.copy(self.childInfo);
                self.overview.date_of_birth = moment(self.overview.date_of_birth).format('MM/DD/YYYY');
                self.overview.program  = self.newEnrollment.program
                self.overview.enrollment_start_date = moment(self.newEnrollment.start_date).format('MM/DD/YYYY');
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

    self.setCurrentStep = function(newStep) {
        self.currentStep = newStep;
    };

    self.openDateOfBirthPicker = function() {
        self.dateOfBirthPickerOpened = ! self.dateOfBirthPickerOpened;
    };

    self.openStartDatePicker = function() {
        self.startDatePickerOpened = ! self.startDatePickerOpened;
    };

    self.getProgramData = function() {
        $http({
            method: 'GET',
            url: '/manageprogram/listprograms'
        }).then(function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            self.programs = [];
            angular.forEach(response.data, function(program) {
                self.programs.push(JSON.parse(program));
            });
        }, function errorCallback(response) {
            // TODO(zilong): deal with error here
        });
    };

    self.$onInit = function() {
        self.dateOfBirthPickerOpened = false;
        self.startDatePickerOpened = false;
        self.resetButton();
        self.getProgramData();
        self.currentStep = 0;
    }

    self.closeModal = function() {
        $uibModalInstance.close();
    }
}
