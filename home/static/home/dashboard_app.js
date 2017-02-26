
DashboardController = function($scope, $http, $window, $location) {
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

DashboardController.prototype.initialize = function() {
	this.http_({
		method: 'GET',
		url: '/home/listprograms'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.programs = [];
	    angular.forEach(response.data, angular.bind(this, function(program) {
	    	this.scope_.programs.push(JSON.parse(program));
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
                 .when('/invoice', {templateUrl: '/static/home/invoice_component_tmpl.html'})
                 .when('/profile', {templateUrl: '/static/home/profile_component_tmpl.html'})
                 .when('/billing', {templateUrl: '/static/home/billing_component_tmpl.html'})
                 .when('/child/list', {template: '<child-list></child-list>'})
                 .when('/child/edit/:childId', {template: '<child-editor></child-editor>'})
                 .otherwise('/dashboard');
          }])
    .controller('DashboardCtrl', DashboardController)
		// to support enrollment modal in child-card
		// need child/child-enrollment.component.js
    .controller('ChildEnrollmentController', ChildEnrollmentController)
		// to support EnrollmentEditorModal
		// need enrollment/enrollment-editor.component.js
		.controller('EnrollmentEditorController', EnrollmentEditorController)
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
    .component('invoicesComponent', {
        templateUrl: '/static/invoice/invoices_component_tmpl.html',
        controller: InvoicesComponentController,
        bindings: {
          invoices: '<'
        }
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
        controller: ['$http', '$location', childListController]
    })
    .component('childCard', {
        templateUrl: '/static/child/child-card.template.html',
        controller : ['$uibModal', '$scope', '$http', '$routeParams', '$location', ChildCardController],
        bindings: {
          child: '<',
          index: '<'
        }
    })
    .component('childForm',{
        templateUrl: '/static/child/child-form.template.html',
        controller : ['$http', '$routeParams', '$location', ChildFormController]
    })
    .component('enrollmentList',{
        templateUrl: '/static/enrollment/enrollment-list.template.html',
        controller : ['$uibModal', '$log', '$http', EnrollmentListController],
        bindings: {
            enrollments: '<',
            child: '<'
        }
    });
