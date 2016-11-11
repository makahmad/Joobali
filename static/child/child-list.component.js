childListController = function ChildListController($http, $routeParams, $location) {
    this.refreshList = function() {
        $http({
            method: 'GET',
            url: '/child/list'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            console.log(response);
            this.childs = [];
            angular.forEach(response.data, angular.bind(this, function(child) {
                this.childs.push(JSON.parse(child));
            }));
            console.log(this.childs);
        }), function errorCallback(response) {
            // TODO(zilong): deal with error here
            console.log(response);
        });
    };

    this.$onInit = function() {
        this.refreshList();
    }
}