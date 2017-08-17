angular.module('password_module', [ 'ui.bootstrap'])
  .controller('credentialsController', ['$scope', '$sce',
    function($scope, $sce) {

//         console.log('credentialsController running');
        $scope.htmlTooltip = $sce.trustAsHtml('<p>Valid Password:</p><ul><li>Min length 8</li>'+
        '<li>Special Character</li><li>Digit</li><li>Lowercase Letter</li><li>Capital Letter</li></ul>');
    }
  ])
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
            scope.minEightChars = isSatisfied(newVal && newVal.length >= 8);
            scope.minDigit = isSatisfied(newVal && /\d/.test(newVal));
            scope.minCapital = isSatisfied(newVal && /[A-Z]/.test(newVal));
            scope.minLower =  isSatisfied(newVal && /[a-z]/.test(newVal));
            scope.minSpecial = isSatisfied(newVal && /(?=.*\W)/.test(newVal));

            scope.strength =  scope.minEightChars +
               scope.minLower +
               scope.minDigit +
               scope.minCapital +scope.minSpecial ;

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
          '</div>Valid Password:'+
          '<div><small>Minimum Length of 8</small> <i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i><i ng-show="minEightChars==0" class="fa fa-circle-o"></i></div>'+
          '<div><small>1 Special Character</small> <i ng-show="minSpecial==1" class="fa fa-check-circle-o"></i><i ng-show="minSpecial==0" class="fa fa-circle-o"></i></div>'+
          '<div><small>1 Number</small> <i ng-show="minDigit==1" class="fa fa-check-circle-o"></i><i ng-show="minDigit==0" class="fa fa-circle-o"></i></div>'+
          '<div><small>1 Lowercase Letter</small> <i ng-show="minLower==1" class="fa fa-check-circle-o"></i><i ng-show="minLower==0" class="fa fa-circle-o"></i></div>'+
          '<div><small>1 Capital Letter</small> <i ng-show="minCapital==1" class="fa fa-check-circle-o"></i><i ng-show="minCapital==0" class="fa fa-circle-o"></i></div>'
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