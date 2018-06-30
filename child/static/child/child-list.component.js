ChildListController = function ChildListController($uibModal, $scope, $http, $routeParams, $location) {

    this.uibModal_ = $uibModal;
    this.http_ = $http;
    this.routeParams_ = $routeParams;
    this.location_ = $location;
    this.programId = this.routeParams_.programId;
    this.programs = [];
    this.parent_emails = new Set();
    this.children = [];

    $scope.non_invited_parents = false;

	self.http_({
	  method: 'GET',
	  url: '/enrollment/listEnrollments'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    angular.forEach(response.data, angular.bind(this, function(enrollment) {
	        enrollment = JSON.parse(enrollment);

            if(enrollment.sent_email_count==0 && enrollment.status=='initialized')
	    	    $scope.non_invited_parents= true;
	    }));

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });

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
        this.parent_emails = new Set();
        angular.forEach(response.data, angular.bind(this, function(child) {
            child_object = JSON.parse(child);
            this.children.push(child_object);
            this.parent_emails.add(child_object.parent_email)
        }));
    }), angular.bind(this, function errorCallback(response) {
        // TODO(zilong): deal with error here
        console.log(response);
    }));
}



ChildListController.prototype.openAddChildModal = function() {
    console.log("Opening Add Enrollment Modal");
    var self = this;

  //  if (this.checkRequirements()) { // Check prerequisites for provider to enroll a child
        var modalInstance = this.uibModal_.open({
            animation: true,
            templateUrl: '/static/child/child-form.template.html',
            controller: 'ChildFormController',
            controllerAs: '$ctrl',
            resolve: {
                parent_emails: function () {
                  return self.parent_emails;
                },
                 check_requirements: this.checkRequirements
            }
        }).closed.then(angular.bind(this, function() {
            this.refreshList();
        }));
  //  }
};


ChildListController.prototype.emailParents = function() {

    console.log("Opening Email Parent Modal");

    bootbox.confirm({
        message: "Send enrollment email to all parents who have never been emailed before?",
        buttons: {
            confirm: {
                label: 'Yes',
                className: 'btn btn-default btn-lg pull-right joobali'
            },
            cancel: {
                label: 'No',
				className: 'btn btn-default btn-lg pull-right'
            }
        },
        callback: angular.bind(this, function(result) {
            if (result === true) {
            console.log("yes");
                this.http_({
                    method: 'POST',
                    url: '/enrollment/emailNonInvitedParents'
                }).then(angular.bind(this, function successCallback(response) {
                        if (response.data == 'success') {
                            bootbox.alert("All non-invited parents emailed successfully.", function() {
                                location.reload();
                            })
                        } else {
                            bootbox.alert(response.data);
                        }
                }), angular.bind(this, function errorCallback(response){
                        console.log('post failed');
                        bootbox.alert("Something wrong happened. Please try again later");
                }));
            }
        })
    });
};



ChildListController.prototype.getProgramData = function() {
    this.http_({
        method: 'GET',
        url: '/manageprogram/listprograms'
    }).then(angular.bind(this, function successCallback(response) {
        // this callback will be called asynchronously
        // when the response is available
        // response.data.shift();
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
//    console.log("running set default filtering program");
    angular.forEach(this.programs, angular.bind(this, function(program) {
        if (program.id == this.programId) {
            this.selectedFilteringProgram = program;
        }
    }));
}
