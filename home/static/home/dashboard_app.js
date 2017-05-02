DashboardController = function($scope, $http, $window, $location, $uibModal) {
	this.http_ = $http;
	this.window_ = $window;
	this.location_ = $location;
	this.scope_ = $scope;
	this.scope_.programs = [];
	this.scope_.fundings = [];
	this.scope_.invoices = [];
	this.scope_.payments = [];
	this.initialize();
	this.scope_.module = '/programs'; //module is used to highlight active left hand nav selection
    this.animationsEnabled = true;

    //IF URL = http://joobali.com/home/dashboard#!/programs GET /programs
    //used for left hand nav menu highlighting
    if ($location.absUrl().split('?')[0].split('!')[1]!=undefined)
        this.scope_.module = $location.absUrl().split('?')[0].split('!')[1];

    this.scope_.changeView = function(view) {
        console.log("changeView(" + view + ")");
        $location.path(view);
        this.module = view;
    }

    this.scope_.openReferralComponentModal = function () {
        var modalInstance = $uibModal.open({
          animation: this.animationsEnabled,
          component: 'referralComponent'
        });
      };



};

DashboardController.prototype.initialize = function() {
	this.http_({
		method: 'GET',
		url: '/home/listprograms'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.programs = [];
	    console.log(response.data);
	    angular.forEach(response.data, angular.bind(this, function(program) {
            program = JSON.parse(program);
            if(program.indefinite)
                program.endDate = "Indefinite";
	    	this.scope_.programs.push(program);
	    }));

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
	    //console.log(response.data);
	    angular.forEach(response.data, angular.bind(this, function(invoice) {
	        invoice.due_date_str = invoice.due_date;
	        invoice.due_date = new Date(invoice.due_date_str);
	    	this.scope_.invoices.push(invoice);
	    }));
	    //console.log(this.scope_.invoices);

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
	    console.log(response.data);
	    angular.forEach(response.data, angular.bind(this, function(payment) {
	    	this.scope_.payments.push(payment);
	    }));
	    console.log(this.scope_.payments);

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
	    console.log(response);
	    angular.forEach(response.data, angular.bind(this, function(funding) {
	    	this.scope_.fundings.push(JSON.parse(funding));
	    }));

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
}

DashboardController.prototype.selectProgram = function(program) {
    for (index in this.scope_.programs) {
        this.scope_.programs[index].selected = false;
    }
    program.selected = true;
    this.location_.path('/program/' + program.id);
}

app = angular.module('dashboardApp', ['ngAnimate','ngSanitize', 'ui.bootstrap', 'ngRoute'])
    .config(['$httpProvider',
        function($httpProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        }])
    .config(['$locationProvider', '$routeProvider',
         function($locationProvider, $routeProvider) {
             $locationProvider.hashPrefix('!');
             $routeProvider
                 .when('/programs', {templateUrl: '/static/home/programs_component_tmpl.html'})
                 .when('/program/:programId', {template: '<edit-program-component programs="programs"></edit-program-component>'})
                 .when('/invoice', {template: '<invoice-component invoices="invoices"></invoice-component>'})
                 .when('/payments', {template: '<payment-component payments="payments"></payment-component>'})
                 .when('/profile', {template: '<profile-component profile="profile"></profile-component>'})
                 .when('/helpcenter', {template: '<helpcenter-component></helpcenter-component>'})
                 .when('/billing', {templateUrl: '/static/home/billing_component_tmpl.html'})
                 .when('/child/list', {template: '<child-list></child-list>'})
                 .when('/child/list/:programId', {template: '<child-list></child-list>'})
                 .when('/child/edit/:childId', {template: '<child-editor></child-editor>'})
                 .otherwise('/programs'); //.otherwise('/dashboard');
          }])
    .controller('DashboardCtrl', DashboardController)
    // to support enrollment modal in child-card
    // need child/child-enrollment.component.js
    .controller('ChildEnrollmentController', ChildEnrollmentController)
    // to support add child modal in child list
    // need child/child-form.component.js
    .controller('ChildFormController', ChildFormController)
    // to support EnrollmentEditorModal
    // need enrollment/enrollment-editor.component.js
    .controller('EnrollmentEditorController', EnrollmentEditorController)
    .controller('AddInvoiceController', AddInvoiceController)
    .controller('InvoiceSettingsController', InvoiceSettingsController)
    .controller('AdjustInvoiceComponentController', AdjustInvoiceComponentController)
    .controller('AddPaymentController', AddPaymentController)
    .component('initSetupComponent', {
        templateUrl: '/static/home/init_setup_component_tmpl.html',
        controller: InitSetupComponentController
    })
    .component('programComponent', {
        templateUrl: '/static/manageprogram/program_component_tmpl.html',
        controller: ProgramComponentController,
        bindings: {
          program: '<'
        }
    })
    .component('addProgramFormComponent', {
        templateUrl: '/static/manageprogram/add_program_form_component_tmpl.html',
        controller: AddProgramFormComponentController,
        bindings: {
          newProgram: '=program'
        }
    })
    .component('addProgramComponent', {
        templateUrl: '/static/manageprogram/add_program_component_tmpl.html',
        controller: AddProgramComponentController
    })
    .component('referralComponent', {
      templateUrl: '/static/referral/referral_component_tmpl.html',
              controller: ReferralComponentController,
      bindings: {
        resolve: '<',
        close: '&',
        dismiss: '&'
      }
    })
    .component('editProgramComponent', {
      templateUrl: '/static/manageprogram/edit_program_component_tmpl.html',
              controller: EditProgramComponentController,
      bindings: {
        programs: '<',
        resolve: '<',
        close: '&',
        dismiss: '&'
      }
    })
    .component('confirmDeleteProgramComponent', {
      templateUrl: '/static/manageprogram/confirm_delete_program_component_tmpl.html',
      controller: ConfirmDeleteProgramComponentController,
      bindings: {
        programs: '<',
        resolve: '<',
        close: '&',
        dismiss: '&'
      }
    })
    .component('addPaymentComponent', {
      templateUrl: '/static/payments/add_payment_component_tmpl.html',
      controller: AddPaymentController,
      bindings: {
        newPayment: '<',
        resolve: '<',
        close: '&',
        dismiss: '&'
      }
    })
    .component('confirmAddPaymentComponent', {
      templateUrl: '/static/payments/confirm_add_payment_component_tmpl.html',
              controller: ConfirmAddPaymentComponentController,
      bindings: {
        newPayment: '<',
        resolve: '<',
        close: '&',
        dismiss: '&'
      }
    })
    // The Invoice page in dashboard
    .component('invoiceComponent', {
        templateUrl: '/static/home/invoice_component_tmpl.html',
        controller: InvoiceComponentController,
        bindings: {
          invoices: '<'
        }
    })
    // The list of invoices inside invoice page
    .component('invoicesComponent', {
        templateUrl: '/static/invoice/invoices_component_tmpl.html',
        controller: InvoicesComponentController,
        bindings: {
          invoices: '<',
          isProvider: '@'
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
    .component('helpcenterComponent', {
        templateUrl: '/static/helpcenter/helpcenter_component_tmpl.html',
        controller: HelpCenterComponentController
    })
    .component('profileComponent', {
        templateUrl: '/static/profile/profile_component_tmpl.html',
        controller: ProfileComponentController,
        bindings: {
          profile: '<'
        }
    })
    .component('fundingsComponent', {
        templateUrl: '/static/funding/fundings_component_tmpl.html',
        controller: FundingsComponentController,
        bindings: {
          fundings: '<'
        }
    })
    .component('transferComponent', {
        templateUrl: '/static/funding/transfer_component_tmpl.html',
        controller: TransferComponentController,
        bindings: {
          fundings: '<'
        }
    })
    .component('addFundingIavComponent', {
        templateUrl: '/static/funding/add_funding_iav_component_tmpl.html',
        controller: AddFundingIavComponentController,
    })
    .component('childList', {
        templateUrl: '/static/child/child-list.template.html',
        controller: ['$uibModal','$http', '$routeParams','$location', ChildListController]
    })
    .component('childCard', {
        templateUrl: '/static/child/child-card.template.html',
        controller : ['$uibModal', '$scope', '$http', '$routeParams', '$location', ChildCardController],
        bindings: {
          child: '<',
          index: '<',
          programs: '<'
        }
    })
    .component('childFormContent', {
        templateUrl: '/static/child/child-form-content.template.html',
        controller: ['$http', ChildFormContentController],
        bindings: {
            programs : '<',
            onSave : '&'
        }
    })
    .component('enrollmentList',{
        templateUrl: '/static/enrollment/enrollment-list.template.html',
        controller : ['$uibModal', '$log', '$http', EnrollmentListController],
        bindings: {
            enrollments: '<',
            child: '<'
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
  ])
  .directive('demoFileModel', function ($parse) {
        return {
            restrict: 'A', //the directive can be used as an attribute only

            /*
             link is a function that defines functionality of directive
             scope: scope associated with the element
             element: element on which this directive used
             attrs: key value pair of element attributes
             */
            link: function (scope, element, attrs) {
                var model = $parse(attrs.demoFileModel),
                    modelSetter = model.assign; //define a setter for demoFileModel

                //Bind change event on the element
                element.bind('change', function () {
                    //Call apply on scope, it checks for value changes and reflect them on UI
                    scope.$apply(function () {
                        //set the model value
                        modelSetter(scope, element[0].files[0]);
                    });
                });
            }
        };
    });

