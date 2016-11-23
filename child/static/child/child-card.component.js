ChildCardController = function ChildCardController($scope, $http, $routeParams, $location) {

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

    this.$onInit = function() {
        console.log("child is " + this.child);
        console.log("index is " + this.index);
        this.getProgramData();
    };
}
