PaymentsComponentController = function($scope, $window, $http) {
    console.log('PaymentsComponentController running');
    this.window_ = $window;
    this.http_ = $http;
    this.sortType = 'date'; // set the default sort type
    this.sortReverse = true;  // set the default sort order
    this.searchTerm = '';     // set the default search/filter term

    $scope.sumPayments = function(payments) {
        let total = 0;
        for (let payment of payments) {
            total += parseFloat(payment.amount);
        }
        return total;
    };
}
