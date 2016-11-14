// Getting Django CSRF token so we can send it within our POST request to Django
// Otherwise, Django denies the request with 403 error.
// https://docs.djangoproject.com/en/dev/ref/csrf/#how-to-use-it
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

FundingController = function($scope, $http) {
	this.scope_ = $scope;
	this.scope_.dwolla = dwolla;
	this.scope_.makeTransfer = function() {
		  var curContent = $("#transferForm");

		  var curInputs = curContent.find("input"),
		  isValid = true;

		      $(".form-group").removeClass("has-error");
		      for(var i=0; i< curInputs.length; i++){
		          if (!curInputs[i].validity.valid){
		              isValid = false;
		              $(curInputs[i]).closest(".form-group").addClass("has-error");
		          }
		      }
		      console.log(isValid);
		  if (isValid) {
		    var source = $('#source :selected').val();
		    var destination = $('#destination :selected').val();
		    var amount = $('#amount').val();
		    var data = {
		    	'source': source,
		    	'destination': destination,
		    	'amount': amount
		    }
		    $http({
			  method: 'POST',
			  url: '/funding/maketransfer',
			  headers: {
			    'X-CSRFToken': csrftoken
			  },
			  data: JSON.stringify(data)
			})
		    .then(
		        function(response){
    		        console.log('post suceeded');
		        }, 
		        function(response){
    		        console.log('post failed');
		        }
		     );
		  }
	};
	this.scope_.handleIAV = angular.bind(this, function() {
	  console.log(this.scope_);
	  console.log(this.scope_.dwolla);
	  console.log(this.scope_.iavToken);
	  console.log(this.scope_);
	  var iavToken = this.scope_.iavToken;
	  this.scope_.dwolla.configure('uat');

	});



    $http({
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

	console.log('init');
    $http({
	  method: 'GET',
	  url: '/funding/getiavtoken'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.iavToken = response.data;
	    console.log(this.scope_.iavToken);
	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });

    $http({
	  method: 'GET',
	  url: '/funding/listprovider'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.scope_.providers = [];
	    angular.forEach(response.data, angular.bind(this, function(provider) {
	    	this.scope_.providers.push(JSON.parse(provider));
	    }));

	  }), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	  });
};

FundingController.prototype.makeTransfer = function() {
  var curContent = $("#transferForm");

  var curInputs = curContent.find("input"),
  isValid = true;

      $(".form-group").removeClass("has-error");
      for(var i=0; i< curInputs.length; i++){
          if (!curInputs[i].validity.valid){
              isValid = false;
              $(curInputs[i]).closest(".form-group").addClass("has-error");
          }
      }
      console.log(isValid);
  if (isValid) {
    console.log($('#source :selected').val());
    console.log($('#destination :selected').val());
    console.log($('#amount').val());
  }
}


app = angular.module('fundingApp', []);
app.controller('FundingCtrl', FundingController);
