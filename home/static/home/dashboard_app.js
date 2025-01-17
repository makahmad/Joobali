DashboardController = function($scope, $http, $window, $location, $uibModal) {
	this.http_ = $http;
	this.window_ = $window;
	this.location_ = $location;
	this.scope_ = $scope;
	this.scope_.programs = [];
	// this.scope_.numberOfPrograms = 0;
	this.scope_.fundings = [];
	this.scope_.invoices = [];
	this.scope_.payments = [];
	this.scope_.numberOfChildren = 0;
	this.scope_.dwollaStatus = 'Unknown';
    this.scope_.selectedProgramFilter = 'Current/Upcoming'
	this.initialize();
    this.animationsEnabled = true;


    this.scope_.programFilters = ['All Programs','Current/Upcoming','Past'];


    self = this;

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
            ga('set', 'page', '/dashboard#!'+view);
            ga('send', 'pageview');
        }
    }


    this.scope_.openReferralComponentModal = function () {
        var modalInstance = $uibModal.open({
          animation: this.animationsEnabled,
          component: 'referralComponent'
        });
      };

    this.scope_.checkRequirements = function() {
//        console.log("Checking provider requirements");

        if (self.scope_.fundings.length == 0) {
           // bootbox.alert("You haven't added any bank account to receive payments. Let's do it now.");
            //self.scope_.changeView('/billing');
            return false;
        } else if (self.scope_.dwollaStatus != 'verified') {
           // bootbox.alert("You haven't add enough profile information to be a verified user. Let's do it now.");
           // self.scope_.changeView('/profile');
            return false;
        }
        return true;
    }



    this.scope_.updateProgramsFilter = function() {

        $http({
            method: 'GET',
            url: '/manageprogram/listprograms',
            params: {'program_filter': this.selectedProgramFilter}
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            $scope.programs = [];
    //	    console.log(response.data);
    //         $scope.numberOfPrograms = JSON.parse(response.data.shift()).count;

            angular.forEach(response.data, angular.bind(this, function(program) {
                program = JSON.parse(program);
                if(program.indefinite)
                    program.endDateStr = "Indefinite";
                $scope.programs.push(program);
            }));

        }), function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response);
        });


//    if (filteringProgram == null) {
//        this.location_.url('/child/list');
//    } else {
//        this.location_.url('/child/list/' + filteringProgram.id);
//    }
}

};

DashboardController.prototype.initialize = function() {
//    this.http_({
//	  method: 'GET',
//	  url: '/login/isinitsetupfinished'
//	}).then(angular.bind(this, function successCallback(response) {
//	    if (response.data == 'false') {
//            var modalInstance = $uibModal.open({
//                animation: true,
//                backdrop: 'static',
//                component: 'initSetupComponent',
//            });
//	    }
//	}), function errorCallback(response) {
//	    // Do nothing
//	});
    this.http_({
	  method: 'GET',
	  url: '/profile/getdwollastatus'
	}).then(angular.bind(this, function successCallback(response) {
	    this.scope_.dwollaStatus = response.data;
	}), function errorCallback(response) {
	    // Do nothing
	});
	this.http_({
		method: 'GET',
		url: '/manageprogram/listprograms',
        params: {'program_filter': this.scope_.selectedProgramFilter}
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.programs = [];
        // this.scope_.numberOfPrograms = JSON.parse(response.data.shift()).count;
//	    console.log(response.data);

	    angular.forEach(response.data, angular.bind(this, function(program) {
            program = JSON.parse(program);
            if(program.indefinite)
                program.endDateStr = "Indefinite";
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
//	    console.log(response.data);
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
	  url: '/payments/listpayments'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.payments = [];
//	    console.log(response.data);
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
	  url: '/funding/listfunding'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.fundings = [];
//	    console.log(response);
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
	  url: '/child/list?'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.numberOfChildren = 0;

	    angular.forEach(response.data, angular.bind(this, function(child) {
	    	this.scope_.numberOfChildren +=1;
	    }));

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });

}



//DashboardController.prototype.selectProgram = function(program) {
//    for (index in this.scope_.programs) {
//        this.scope_.programs[index].selected = false;
//    }
//    program.selected = true;
//    this.location_.path('/program/' + program.id);
//}




app = angular.module('dashboardApp', ['ngAnimate','ngSanitize', 'ui.bootstrap', 'ngRoute', 'ng-currency', 'joobali.base','xeditable'])
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
                 .when('/programs', {templateUrl: '/static/home/programs_component_tmpl.html'})
                 .when('/program/:programId', {template: '<edit-program-component programs="programs"></edit-program-component>'})
                 .when('/invoice', {template: '<invoice-component invoices="invoices" dwolla-status="{{this.dwollaStatus}}" funding-sources="{{this.fundings.length}}"></invoice-component>'})
                 .when('/payments', {template: '<payment-component payments="payments"></payment-component>'})
                 .when('/profile', {template: '<profile-component profile="profile"></profile-component>'})
                 .when('/verification', {template: '<verification-component profile="profile"></verification-component>'})
                 .when('/billing', {template: '<billing-component  fundings="fundings"></billing-component>'})
                 .when('/child/list', {template: '<child-list check-requirements="checkRequirements()" dwolla-status="{{this.dwollaStatus}}" funding-sources="{{this.fundings.length}}"></child-list>'})
                 .when('/child/list/:programId', {template: '<child-list check-requirements="checkRequirements()" dwolla-status="{{this.dwollaStatus}}" funding-sources="{{this.fundings.length}}"></child-list>'})
                 .when('/child/edit/:childId', {template: '<child-editor></child-editor>'})
                 .when('/home', {templateUrl: '/static/home/home.html'})
                 .otherwise('/home');
          }])
    .filter('childAgeFilter', function() {
        return function(children, minAge, maxAge) {
            if (!children) {
                return [];
            }
            var minDuration = null;
            var maxDuration = null;
            if (minAge) {
                tokens = minAge.split(" ");
                if (tokens.length == 2) {
                    minDuration = moment.duration(parseInt(tokens[0]), tokens[1])
//                    console.log(minDuration);
                }
            }
            if (maxAge) {
                tokens = maxAge.split(" ");
                if (tokens.length == 2) {
                    maxDuration = moment.duration(parseInt(tokens[0]), tokens[1]);
//                    console.log(maxDuration);
                }
            }
            var currentDate = moment(new Date());
            var result = [];
            for (var i = 0; i < children.length; i++) {
                var child = children[i];
                var child_age = moment.duration(currentDate.diff(moment(child.date_of_birth, "MM/DD/YYYY")));
                if (minDuration) {
                    if (child_age <= minDuration) {
                        continue;
                    }
                }

                if (maxDuration) {
                    if (child_age > maxDuration) {
                        continue;
                    }
                }
                result.push(child);
            }
            return result;
        }
    })
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
    .controller('EnrollmentResendInvitationDialogController', EnrollmentResendInvitationDialogController)
    .controller('AddInvoiceController', AddInvoiceController)
    .controller('InvoiceSettingsController', InvoiceSettingsController)
    .controller('AddPaymentController', AddPaymentController)
    .component('initSetupComponent', {
        templateUrl: '/static/home/init_setup_component_tmpl.html',
        controller: InitSetupComponentController,
        bindings: {
            close: '&',
            dismiss: '&'
        }
    })
    .component('billingComponent', {
        templateUrl: '/static/home/billing_component_tmpl.html',
        controller: BillingComponentController,
        bindings: {
          fundings: '<'
        }
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
    .component('confirmCopyProgramComponent', {
      templateUrl: '/static/manageprogram/confirm_copy_program_component_tmpl.html',
      controller: ConfirmCopyProgramComponentController,
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
          invoices: '<',
          dwollaStatus : '@',
          fundingSources : '@'
        }
    })
    // The Invoice page in dashboard
    .component('adjustInvoiceComponent', {
        templateUrl: '/static/invoice/adjust_invoice_component_tmpl.html',
        controller: AdjustInvoiceComponentController,
        bindings: {
          resolve: '<',
          close: '&',
          dismiss: '&'
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
          payments: '<',
          isProvider: '@'
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
    .component('profileComponent', {
        templateUrl: '/static/profile/profile_component_tmpl.html',
        controller: ProfileComponentController,
        bindings: {
          profile: '<'
        }
    })
    .component('verificationComponent', {
        templateUrl: '/static/profile/verification_component_tmpl.html',
        controller: VerificationComponentController,
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
        bindings: {
          resolve: '<',
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
    .component('childList', {
        templateUrl: '/static/child/child-list.template.html',
        controller: ['$uibModal','$scope','$http', '$routeParams','$location', ChildListController],
        bindings: {
            checkRequirements : '<',
            dwollaStatus : '@',
            fundingSources : '@'
        }
    })
    .component('childCard', {
        templateUrl: '/static/child/child-card.template.html',
        controller : ['$uibModal', '$scope', '$http', '$routeParams', '$location', 'EnrollmentDateChecker', ChildCardController],
        bindings: {
          checkRequirements : '<',
          child: '<',
          index: '<',
          programs: '<'
        }
    })
    .component('childFormContent', {
        templateUrl: '/static/child/child-form-content.template.html',
        controller: ['$http', 'EnrollmentDateChecker', ChildFormContentController],
        bindings: {
            emails: '<',
            checkRequirements : '<',
            programs : '<',
            onSave : '&',
            onClose : '&'
        }
    })
    .component('enrollmentList',{
        templateUrl: '/static/enrollment/enrollment-list.template.html',
        controller : ['$uibModal', '$log', '$http', EnrollmentListController],
        bindings: {
            enrollments: '<',
            checkRequirements : '<',
            child: '<'
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

