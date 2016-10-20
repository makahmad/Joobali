'use strict';

angular.module('enrollmentApp', ['ngRoute'])
    .config(['$httpProvider',
        function($httpProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        }])
    .config(['$locationProvider', '$routeProvider',
        function($locationProvider, $routeProvider) {
            $locationProvider.hashPrefix('!');
            $routeProvider
                .when('/view', {template: '<enrollment></enrollment>'})
                .when('/edit/:enrollmentId', {template: '<enrollment-editor></enrollment-editor>'})
                .otherwise('/view');
        }]);

