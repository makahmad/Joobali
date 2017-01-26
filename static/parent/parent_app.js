ParentController = function($scope, $http, $window, $location) {
	this.http_ = $http;
	this.window_ = $window;
	this.location_ = $location;
	this.scope_ = $scope;
	this.scope_.programs = [];
	this.scope_.fundings = [];
	this.scope_.invoices = [];

	this.initialize();

    $scope.changeView = function(view) {
        console.log("changeView(" + view + ")");
        $location.path(view);
    }
};

ParentController.prototype.initialize = function() {
	this.http_({
	  method: 'GET',
	  url: '/invoice/listinvoices'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.invoices = [];
	    console.log(response.data);
	    angular.forEach(response.data, angular.bind(this, function(invoice) {
	    	this.scope_.invoices.push(invoice);
	    }));

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
	this.http_({
	  method: 'GET',
	  url: '/funding/listfunding'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.fundings = [];
	    angular.forEach(response.data, angular.bind(this, function(funding) {
	    	this.scope_.fundings.push(JSON.parse(funding));
	    }));
        console.log(this.scope_.fundings);
	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
}

app = angular.module('parentApp', ['ngAnimate','ngSanitize', 'ui.bootstrap', 'ngRoute'])
    .config(['$httpProvider',
        function($httpProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        }])
    .config(['$locationProvider', '$routeProvider',
         function($locationProvider, $routeProvider) {
             $locationProvider.hashPrefix('!');
             $routeProvider
                 .when('/funding', {templateUrl: '/static/parent/funding_component_tmpl.html'})
                 .when('/due', {templateUrl: '/static/parent/pay_bill_component_tmpl.html'})
                 .when('/child/list', {template: '<child-list></child-list>'})
                 .when('/child/edit/:childId', {template: '<child-editor></child-editor>'})
                 .otherwise('/index');
          }])
    .controller('ParentCtrl', ParentController)
    .component('initSetupComponent', {
        templateUrl: '/static/parent/init_setup_component_tmpl.html',
        controller: InitSetupComponentController
    })
    .component('invoicesComponent', {
        templateUrl: '/static/invoice/invoices_component_tmpl.html',
        controller: InvoicesComponentController,
        bindings: {
          invoices: '<'
        }
    })
    .component('fundingsComponent', {
        templateUrl: '/static/funding/fundings_component_tmpl.html',
        controller: FundingsComponentController,
        bindings: {
          fundings: '<'
        }
    })
    .component('makePaymentComponent', {
        templateUrl: '/static/funding/make_payment_component_tmpl.html',
        controller: MakePaymentComponentController,
        bindings: {
          fundings: '<',
          invoices: '<'
        }
    })
    .component('addFundingIavComponent', {
        templateUrl: '/static/funding/add_funding_iav_component_tmpl.html',
        controller: AddFundingIavComponentController,
    })
    .component('childList', {
        templateUrl: '/static/child/child-list.template.html',
        controller: ['$http', '$location', childListController]
    })
    .component('childCard', {
        templateUrl: '/static/child/child-card.template.html',
        controller : ['$scope', '$http', '$routeParams', '$location', ChildCardController],
        bindings: {
          child: '<',
          index: '<'
        }
    });

