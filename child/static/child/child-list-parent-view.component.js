ChildListParentViewController = function ChildListParentViewController($http, $location) {
    var self = this;
    this.refreshList = function() {
        $http({
            method: 'GET',
            url: '/child/list'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            // console.log(response);
            this.children = [];
            angular.forEach(response.data, angular.bind(this, function(child) {
                this.children.push(JSON.parse(child));
            }));
            // console.log(this.children);
        }), function errorCallback(response) {
            // TODO(zilong): deal with error here
            console.log(response);
        });
    };

    self.$onInit = function() {
        self.refreshList();
    }
}