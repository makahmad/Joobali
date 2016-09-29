angular.
module('enrollmentApp').
component('enrollmentForm', {
    templateUrl: '/static/enrollment/enrollment-form.template.html',
    controller: ['$http',
        function EnrollmentFormController($http) {
            console.log('EnrollmentFormController running');
            this.form = {};

            this.handleDone = function() {
            };
            this.handleSave = function() {
                console.log("save");
                console.log(this.form);
                $http.post('/enrollment/add', this.form).then(function successCallback(response) {
                    console.log(response);
                    // TODO(zilong): progress through successful submission
                }, function errorCallback(response) {

                });
            };

            this.handleNext = function() {
              console.log($(".form-content.active"));
              var curContent = $(".form-content.active");
              var curNav = $(".form-nav.active");

              var curInputs = curContent.find("input");
              isValid = true;
              $(".form-group").removeClass("has-error");
              for(var i=0; i< curInputs.length; i++){
                  console.log(curInputs[i].validity.valid);
                  if (!curInputs[i].validity.valid){
                      isValid = false;
                      $(curInputs[i]).closest(".form-group").addClass("has-error");
                  }
              }
              console.log(isValid);

              if (isValid) {
                curNav.removeClass("active");
                curNav.next().addClass("active");
                curContent.removeClass("active").hide();
                curContent.next().addClass("active").show();

                if (curNav.next().attr('id') === "navStep2") {
                  $("#nextButton").toggle();
                  $("#saveButton").toggle();
                }
              }
            };
        }
    ]
});
