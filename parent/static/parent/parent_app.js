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
                 .when('/profile', {template: '<profile></profile>'})
                 .when('/child/list', {template: '<child-list></child-list>'})
                 .when('/child/edit/:childId', {template: '<child-editor></child-editor>'})
                 .otherwise('/index');
          }])
    .controller('ParentCtrl', ParentController)
	.component('initSetupComponent', {
        templateUrl: '/static/parent/init_setup_component_tmpl.html',
        controller: InitSetupComponentController
    })
    .component('autopaySetupFormComponent', {
        templateUrl: '/static/parent/autopay_setup_form_component_tmpl.html',
        controller: AutopaySetupFormComponentController,
        bindings: {
            data: '<',
        }
    })
	.component('initSetupConfirmFormComponent', {
        templateUrl: '/static/parent/init_setup_confirm_form_component_tmpl.html',
        bindings: {
            data: '<',
        }
    })
    .component('paymentSetupComponent', {
        templateUrl: '/static/parent/payment_setup_component_tmpl.html',
        controller: PaymentSetupComponentController
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
    .component('profile', {
        templateUrl: '/static/parent/profile_component_tmpl.html',
        controller: ProfileComponentController
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
    })
    .directive('passwordStrength', [
    function() {
      return {
        require: 'ngModel',
        restrict: 'E',
        scope: {
          password: '=ngModel'
        },

        link: function(scope, elem, attrs, ctrl) {
          scope.$watch('password', function(newVal) {

            scope.strength = isSatisfied(newVal && newVal.length >= 8) +
              isSatisfied(newVal && /[a-z]/.test(newVal)) +
              isSatisfied(newVal && /[A-Z]/.test(newVal)) +
              isSatisfied(newVal && /(?=.*\W)/.test(newVal)) +
              isSatisfied(newVal && /\d/.test(newVal));

            function isSatisfied(criteria) {
              return criteria ? 1 : 0;
            }
          }, true);
        },
        template: '<div class="progress">' +
          '<div class="progress-bar progress-bar-danger" style="width: {{strength >= 1 ? 25 : 0}}%"></div>' +
          '<div class="progress-bar progress-bar-warning" style="width: {{strength >= 2 ? 25 : 0}}%"></div>' +
          '<div class="progress-bar progress-bar-warning" style="width: {{strength >= 3 ? 25 : 0}}%"></div>' +
          '<div class="progress-bar progress-bar-success" style="width: {{strength >= 5 ? 25 : 0}}%"></div>' +
          '</div>'
      }
    }
  ])
  .directive('patternValidator', [
    function() {
      return {
        require: 'ngModel',
        restrict: 'A',
        link: function(scope, elem, attrs, ctrl) {
          ctrl.$parsers.unshift(function(viewValue) {

            var patt = new RegExp(attrs.patternValidator);

            var isValid = patt.test(viewValue);

            ctrl.$setValidity('passwordPattern', isValid);

            // angular does this with all validators -> return isValid ? viewValue : undefined;
            // But it means that the ng-model will have a value of undefined
            // So just return viewValue!
            return viewValue;

          });
        }
      };
    }
  ]);


