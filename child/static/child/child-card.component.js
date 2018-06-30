ChildCardController = function ChildCardController($uibModal, $scope, $http, $routeParams, $location, EnrollmentDateChecker) {
    this.uibModal_ = $uibModal;
    this.scope_ = $scope;
    this.http_ = $http;
    this.routeParams_ = $routeParams;
    this.location_ = $location;
    this.enrollmentDateChecker_ = EnrollmentDateChecker;
    this.todayDate = new Date();

    $scope.opened = {};
	$scope.open = function($event, elementOpened) {
		$event.preventDefault();
		$event.stopPropagation();

		$scope.opened[elementOpened] = !$scope.opened[elementOpened];
	};
}

ChildCardController.prototype.$onInit = function() {
    this.getEnrollmentData();
    var currentDate = moment(new Date());
    var dateDiff = moment.duration(currentDate.diff(moment(this.child.date_of_birth, "MM/DD/YYYY")));

    if (this.child.date_of_birth!=null)
        this.child.date_of_birth = new Date(this.child.date_of_birth);

    diff_str = "";
    if (dateDiff.years() > 0) {
        diff_str += dateDiff.years() + " years, "
    }
    if (dateDiff.months() > 0) {
        diff_str += dateDiff.months() + " months, "
    }
    if (dateDiff.days() > 0) {
        diff_str += dateDiff.days() + " days"
    }
    this.child.age = diff_str;
};

ChildCardController.prototype.isRemovable = function() {

    result = true;
    angular.forEach(this.enrollments, function(enrollment) {
        if (enrollment.enrollment.status == 'active') {
            result = false;
        }
    })
    if (this.child.parent_status == 'active') {
        result = false;
    }
    return result

};

ChildCardController.prototype.removeChild = function() {
    console.log(this.child);

    bootbox.confirm({
        message: "Are you sure you want to remove this child (" + this.child.first_name + ")?",
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
                this.http_({
                    method: 'POST',
                    url: '/child/remove',
                    data: JSON.stringify(this.child)
                }).then(angular.bind(this, function successCallback(response) {
                        if (response.data == 'success') {
                            bootbox.alert("Child removed successfully.", function() {
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

ChildCardController.prototype.updateChild = function(data) {

    if (this.child.date_of_birth!=null)
        this.child.date_of_birth =  moment(this.child.date_of_birth).format('MM/DD/YYYY');
    else
        return "Date of birth is required";

    this.http_({
        method: 'POST',
        url: '/child/update',
        data: JSON.stringify(this.child)
    }).then(angular.bind(this, function successCallback(response) {
            this.$onInit();
    }), angular.bind(this, function errorCallback(response){
            console.log('post failed');
            bootbox.alert("Something is wrong with the saving. Please try again later");
    }));

};

ChildCardController.prototype.openEnrollmentModal = function() {
    console.log("Opening Add Enrollment Modal");
    var self = this;
    var modalInstance = this.uibModal_.open({
        animation: true,
        templateUrl: '/static/child/child-enrollment.template.html',
        controller: 'ChildEnrollmentController',
        controllerAs: '$ctrl',
        resolve: {
            enrollmentDateChecker: function() {
                return self.enrollmentDateChecker_;
            },
            child: function() {
                return self.child;
            },
            programs: function() {
                return self.programs;
            },
            checkRequirements: this.checkRequirements
        }
    });

    modalInstance.result.then(angular.bind(this, function(data) {
        console.log("data is %s", angular.toJson(data));
        if (data.enrollmentStatus === 'success') {
            this.getEnrollmentData();
        }
    }), angular.bind(this, function() {
        console.log('Modal dismissed at: ' + new Date());
    }));
};

ChildCardController.prototype.getChild = function() {
    return this.child;
}

ChildCardController.prototype.getPrograms = function() {
    return this.programs;
}


ChildCardController.prototype.getEnrollmentData = function() {
    this.http_.post('/enrollment/listByChildId', { 'child_id' : this.child.id })
    .then(angular.bind(this, function successCallback(response) {
        this.enrollments = [];
        angular.forEach(response.data, angular.bind(this, function(enrollment) {

	        enrollment = JSON.parse(enrollment);
            if(enrollment.enrollment.sent_email_count==0 && enrollment.enrollment.status=='initialized')
	    	    enrollment.enrollment.status = 'pre-initialized'

            this.enrollments.push(enrollment);
        }));
    }), angular.bind(this, function errorCallback(response){
    }));
};