angular.module('password_module', [ 'ui.bootstrap'])
  .controller('credentialsController', ['$scope', '$sce',
    function($scope, $sce) {
            function isSatisfied(criteria) {
              return criteria ? 1 : 0;
            }

            function createPasswordTooltip(newVal) {

                tooltip = 'Valid Password:';

                minEightChars = isSatisfied(newVal && newVal.length >= 8);
                minDigit = isSatisfied(newVal && /\d/.test(newVal));
                minCapital = isSatisfied(newVal && /[A-Z]/.test(newVal));
                minLower =  isSatisfied(newVal && /[a-z]/.test(newVal));
                minSpecial = isSatisfied(newVal && /(?=.*\W)/.test(newVal));

                if(minEightChars==1)
                    tooltip +='<div><i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i> <small>Minimum Length of 8</small></div>';
                else
                    tooltip +='<div><i ng-show="minEightChars==0" class="fa fa-circle-o"></i> <small>Minimum Length of 8</small></div>';

                if(minSpecial==1)
                    tooltip +='<div><i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i> <small>1 Special Character</small></div>';
                else
                    tooltip +='<div><i ng-show="minEightChars==0" class="fa fa-circle-o"></i> <small>1 Special Character</small></div>';

                if(minCapital==1)
                    tooltip +='<div><i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i> <small>1 Capital Letter</small></div>';
                else
                    tooltip +='<div><i ng-show="minEightChars==0" class="fa fa-circle-o"></i> <small>1 Capital Letter</small></div>';

                if(minLower==1)
                    tooltip +='<div><i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i> <small>1 Lowercase Letter</small></div>';
                else
                    tooltip +='<div><i ng-show="minEightChars==0" class="fa fa-circle-o"></i> <small>1 Lowercase Letter</small></div>';

                if(minDigit==1)
                    tooltip +='<div><i ng-show="minEightChars==1" class="fa fa-check-circle-o"></i> <small>1 Number</small></div>';
                else
                    tooltip +='<div><i ng-show="minEightChars==0" class="fa fa-circle-o"></i> <small>1 Number</small></div>';

              return tooltip;
            }


        $scope.htmlTooltip = '';

          $scope.$watch('password', function(newVal) {
            $scope.htmlTooltip = $sce.trustAsHtml( createPasswordTooltip(newVal) );
          });
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