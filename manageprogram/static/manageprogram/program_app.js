app = angular.module('programApp', []);

app.controller('ProgramCtrl', function($scope) {
    $scope.num = 0;
    $scope.programs = [{"name":"haha", "fee":"12"}, {"name":"haha11", "fee":"13"}];
});