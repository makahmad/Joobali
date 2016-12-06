ChildCardController = function ChildCardController($scope, $http, $routeParams, $location) {

    // TODO(zilong): Move this to ChildListController
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

    this.getEnrollmentData = function() {
        request = {
            'child_id' : this.child.id,
            'parent_email': this.child.parent_email
        }
        $http.post('/enrollment/listByChildId', request).then(angular.bind(this, function successCallback(response) {
            this.enrollments = [];
            console.log('enrollment/listByChild: ' + response.data)
            angular.forEach(response.data, angular.bind(this, function(enrollment) {
                this.enrollments.push(JSON.parse(enrollment));
            }));
        }), angular.bind(this, function errorCallback(response){
        }));
    }

    this.$onInit = function() {
        console.log("child is " + JSON.stringify(this.child));
        console.log("index is " + this.index);
        this.getProgramData();
        this.getEnrollmentData();
    };
}
