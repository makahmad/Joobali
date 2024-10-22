ParentController = function($scope, $http, $window, $location, $uibModal) {
	this.http_ = $http;
	this.window_ = $window;
	this.location_ = $location;
	this.scope_ = $scope;
	this.scope_.programs = [];
	this.scope_.fundings = [];
	this.scope_.invoices = [];
	this.scope_.payments = [];
//	this.scope_.announcementCount = 4; TODO mak testing announcements
	this.scope_.hasEnrollment = false;
	this.initialize($uibModal);
    this.animationsEnabled = true;

    //controls highlighting of left hand menu items
    this.scope_.isActive = function (viewLocation) {
         var active = $location.path().indexOf(viewLocation) >=0;
         return active;
    };

    this.scope_.changeView = function(view) {
        $location.path(view);

        $( "#myNavbar" ).removeClass('in');  //collapse mobile menu when switching pages

        //Google Analytics code to detect view changes
        if (typeof ga != 'undefined')
        {
            ga('set', 'page', '/parent/#!'+view);
            ga('send', 'pageview');
        }
    }

    this.scope_.openReferralComponentModal = function () {
        var modalInstance = $uibModal.open({
          animation: this.animationsEnabled,
          component: 'referralComponent'
        });
      };
};

ParentController.prototype.initialize = function($uibModal) {
    this.http_({
	  method: 'GET',
	  url: '/login/isinitsetupfinished'
	}).then(angular.bind(this, function successCallback(response) {
	    if (response.data == 'false') {
            var modalInstance = $uibModal.open({
                animation: true,
                backdrop: 'static',
                component: 'initSetupComponent',
            });
	    }
	}), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	});
	this.http_({
	  method: 'GET',
	  url: '/invoice/listinvoices'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.invoices = [];
	    // console.log(response.data);
	    angular.forEach(response.data, angular.bind(this, function(invoice) {
	    	invoice.due_date_str = invoice.due_date;
	        invoice.due_date = new Date(invoice.due_date_str);
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
//	    console.log(response.data);
	    angular.forEach(response.data, angular.bind(this, function(funding) {
	    	this.scope_.fundings.push(JSON.parse(funding));
	    }));

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
	this.http_({
	  method: 'GET',
	  url: '/payments/listpayments'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.payments = [];
	    // console.log(response.data);

	    angular.forEach(response.data, angular.bind(this, function(payment) {
	        var paymentDate = new Date(payment.date);
            payment.date = paymentDate;
	    	this.scope_.payments.push(payment);
	    }));

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
	this.http_({
	  method: 'GET',
	  url: '/parent/hasenrollment'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.hasEnrollment = response.data;

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
}

app = angular.module('parentApp', ['ngAnimate','ngSanitize', 'ui.bootstrap', 'ngRoute', 'ng-currency','xeditable'])
    .run(function(editableOptions) {
          editableOptions.theme = 'bs3';
        })
    .config(['$httpProvider',
        function($httpProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        }])
    .config(['$locationProvider', '$routeProvider',
         function($locationProvider, $routeProvider) {
             $locationProvider.hashPrefix('!');
             $routeProvider
                 .when('/funding', {template: '<funding-component fundings="fundings"></funding-component>'})
                 .when('/due', {templateUrl: '/static/parent/pay_bill_component_tmpl.html'})
                 .when('/payments', {templateUrl: '/static/parent/payment_component_tmpl.html'})
                 .when('/profile', {template: '<profile></profile>'})
                 .when('/child/list', {template: '<child-list-parent-view></child-list-parent-view>'})
                 .when('/child/edit/:childId', {template: '<child-editor></child-editor>'})
                 .when('/enrollmentview/:providerId/:enrollmentId', {template: '<enrollment-parent-view></enrollment-parent-view>'})
                 .when('/home', {templateUrl: '/static/parent/home.html'})
                 .otherwise('/home'); //.otherwise('/index');
          }])
    .controller('ParentCtrl', ParentController)
    .controller('EnrollmentAcceptanceDialogController', EnrollmentAcceptanceDialogController)
	.component('initSetupComponent', {
        templateUrl: '/static/parent/init_setup_component_tmpl.html',
        controller: InitSetupComponentController,
        bindings: {
            resolve: '<',
            close: '&',
            dismiss: '&'
        }
    })
    .component('fundingComponent', {
        templateUrl: '/static/parent/funding_component_tmpl.html',
        controller: FundingComponentController,
        bindings: {
          fundings: '<',
        }
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
        controller: PaymentSetupComponentController,
        bindings: {
            resolve: '<',
            close: '&',
            dismiss: '&'
        }
    })
    .component('invoicesComponent', {
        templateUrl: '/static/invoice/invoices_component_tmpl.html',
        controller: InvoicesComponentController,
        bindings: {
          fundings: '<',
          invoices: '<'
        }
    })
    .component('referralComponent', {
      templateUrl: '/static/parent/referral_component_tmpl.html',
              controller: ReferralComponentController,
      bindings: {
        resolve: '<',
        close: '&',
        dismiss: '&'
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
    // The Payments page in dashboard
    .component('paymentComponent', {
        templateUrl: '/static/home/payment_component_tmpl.html',
        controller: PaymentComponentController,
        bindings: {
          payments: '<'
        }
    })
    // The list of payments inside payments page
    .component('paymentsComponent', {
        templateUrl: '/static/payments/payments_component_tmpl.html',
        controller: PaymentsComponentController,
        bindings: {
          payments: '<',
          isProvider: '@'
        }
    })
    .component('addFundingIavComponent', {
        templateUrl: '/static/funding/add_funding_iav_component_tmpl.html',
        controller: AddFundingIavComponentController,
        bindings: {
            close: '&',
            dismiss: '&'
        }
    })
    .component('verifyMicroDepositsComponent', {
      templateUrl: '/static/funding/verify_micro_deposits_component_tmpl.html',
      controller: VerifyMicroDepositsComponentController,
      bindings: {
        resolve: '<',
        close: '&',
        dismiss: '&'
      }
    })
    .component('profile', {
        templateUrl: '/static/parent/profile_component_tmpl.html',
        controller: ProfileComponentController
    })
    .component('enrollmentParentView', {
        templateUrl: '/static/enrollment/enrollment-parent-view.template.html',
        controller: ['$uibModal', '$log', '$http', '$routeParams', '$location', '$timeout', EnrollmentParentViewController]
    })
    .component('childListParentView', {
        templateUrl: '/static/child/child-list-parent-view.template.html',
        controller: ['$http', '$location', ChildListParentViewController]
    })
    .component('childCardParentView', {
        templateUrl: '/static/child/child-card-parent-view.template.html',
        controller : ['$scope', '$http', ChildCardParentViewController],
        bindings: {
          child: '<',
          index: '<'
        }
    })
    .component('enrollmentListParentView', {
        templateUrl: '/static/enrollment/enrollment-list-parent-view.template.html',
        controller: ['$location', EnrollmentListParentViewController],
        bindings: {
            child : '<',
            enrollments : '<'
        }
    })
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


