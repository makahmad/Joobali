PaymentsComponentController = function($window, $http) {
    console.log('PaymentsComponentController running');
    this.window_ = $window;
    this.http_ = $http;
    this.sortType = 'child'; // set the default sort type
    this.sortReverse = false;  // set the default sort order
    this.searchTerm = '';     // set the default search/filter term
    console.log(this.isProvider);
}
