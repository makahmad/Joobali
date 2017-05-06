ChildListController = function ChildListController($uibModal, $http, $routeParams, $location) {
    this.uibModal_ = $uibModal;
    this.http_ = $http;
    this.routeParams_ = $routeParams;
    this.location_ = $location;
    this.programId = this.routeParams_.programId;
    this.programs = [];
}

ChildListController.prototype.$onInit = function() {
    this.refreshList();
    this.getProgramData();
}

ChildListController.prototype.refreshList = function() {
    request_url = '/child/list?';
    console.log('this.programId: ' + this.programId);
    if (this.programId) {
        request_url += ('programId=' + this.programId);
    }
    this.http_({
        method: 'GET',
        url: request_url
    }).then(angular.bind(this, function successCallback(response) {
        // this callback will be called asynchronously
        // when the response is available
        this.children = [];
        angular.forEach(response.data, angular.bind(this, function(child) {
            this.children.push(JSON.parse(child));
        }));
    }), angular.bind(this, function errorCallback(response) {
        // TODO(zilong): deal with error here
        console.log(response);
    }));
}



ChildListController.prototype.openAddChildModal = function() {
    console.log("Opening Add Enrollment Modal");
    var modalInstance = this.uibModal_.open({
        animation: true,
        templateUrl: '/static/child/child-form.template.html',
        controller: 'ChildFormController',
        controllerAs: '$ctrl',
    }).closed.then(angular.bind(this, function() {
        this.refreshList();
    }));
};

ChildListController.prototype.getProgramData = function() {
    this.http_({
        method: 'GET',
        url: '/manageprogram/listprograms'
    }).then(angular.bind(this, function successCallback(response) {
        // this callback will be called asynchronously
        // when the response is available
        this.programs = [];
        angular.forEach(response.data, angular.bind(this, function(program) {
            this.programs.push(JSON.parse(program));
            this.setDefaultFilteringProgram();
        }));
    }), angular.bind(function errorCallback(response) {
        // TODO(zilong): deal with error here
    }));
};

ChildListController.prototype.updateFilteringProgram = function() {
    filteringProgram = this.selectedFilteringProgram;
    console.log('filteringProgram is: ' + angular.toJson(filteringProgram));
    if (filteringProgram == null) {
        this.location_.url('/child/list');
    } else {
        this.location_.url('/child/list/' + filteringProgram.id);
    }
}

ChildListController.prototype.setDefaultFilteringProgram = function() {
    console.log("running set default filtering program");
    angular.forEach(this.programs, angular.bind(this, function(program) {
        if (program.id == this.programId) {
            this.selectedFilteringProgram = program;
        }
    }));
}
