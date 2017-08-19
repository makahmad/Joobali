ChildCardParentViewController = function ChildCardParentViewController($http) {
    this.http_ = $http;
    this.enrollments = [];
}

ChildCardParentViewController.prototype.getEnrollmentData = function() {
    this.http_.post('/enrollment/listByChildId', { 'child_id' : this.child.id })
    .then(angular.bind(this, function successCallback(response) {
        this.enrollments = [];
        angular.forEach(response.data, angular.bind(this, function(enrollment) {
            this.enrollments.push(JSON.parse(enrollment));
        }));
    }), angular.bind(this, function errorCallback(response){
    }));
}

ChildCardParentViewController.prototype.$onInit = function() {
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
}