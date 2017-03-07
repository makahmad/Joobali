ChildCardParentViewController = function ChildCardParentViewController($http) {

    var self = this;

    self.getEnrollmentData = function() {
        $http.post('/enrollment/listByChildId', { 'child_id' : this.child.id })
        .then(angular.bind(this, function successCallback(response) {
            this.enrollments = [];
            console.log('enrollment/listByChild: ' + response.data)
            angular.forEach(response.data, angular.bind(this, function(enrollment) {
                this.enrollments.push(JSON.parse(enrollment));
            }));
        }), angular.bind(this, function errorCallback(response){
        }));
    };

    self.$onInit = function() {
        this.getEnrollmentData();
    };
}