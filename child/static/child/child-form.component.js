ChildFormController = function ChildFormController($uibModalInstance, $http, parent_emails) {

    this.parent_emails = Array.from(parent_emails);
    this.programs = {};
    this.http_ = $http;
    this.uibModalInstance_ = $uibModalInstance;

    this.doneButton = {};

    this.doneButton.click = angular.bind(this, function() {
        this.closeModal();
    });
    console.log(this.parent_emails);
}


ChildFormController.prototype.resetButton = function() {
    this.doneButton.show = false;
};

ChildFormController.prototype.resetModal = function() {
    this.resetButton();
}

ChildFormController.prototype.getPrograms = function() {
    this.http_({
        method: 'GET',
        url: '/manageprogram/listprograms'
    }).then(angular.bind(this, function successCallback(response) {
        // this callback will be called asynchronously
        // when the response is available
        this.programs = [];
        angular.forEach(response.data, angular.bind(this, function(program) {
            this.programs.push(JSON.parse(program));
        }));
    }), angular.bind(this, function errorCallback(response) {
        // TODO(zilong): deal with error here
    }));
};

ChildFormController.prototype.$onInit = function() {
    this.resetButton();
    this.getPrograms();
}

ChildFormController.prototype.closeModal = function() {
    this.uibModalInstance_.close();
}

ChildFormController.prototype.onSave = function(isSaved) {
    this.isSaved = isSaved;
    if (this.isSaved) {
        this.doneButton.show = true;
    } else {
        this.doneButton.show = false;
    }
}