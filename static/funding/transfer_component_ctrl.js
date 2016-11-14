TransferComponentController = function($location, $http) {
    console.log('TransferComponentController running');
    this.location_ = $location;
    this.http_ = $http;

    this.fetchProviders();
}

TransferComponentController.prototype.fetchProviders = function() {
    this.http_({
	  method: 'GET',
	  url: '/funding/listprovider'
	}).then(angular.bind(this, function successCallback(response) {
	    // this callback will be called asynchronously
	    // when the response is available
	    this.providers = [];
	    angular.forEach(response.data, angular.bind(this, function(provider) {
	    	this.providers.push(JSON.parse(provider));
	    }));

	}), function errorCallback(response) {
	    // called asynchronously if an error occurs
	    // or server returns response with an error status.
	    console.log(response);
	});
}

TransferComponentController.prototype.makeTransfer = function() {

      if (this.validate()) {
        var source = $('#source :selected').val();
        var destination = $('#destination :selected').val();
        var amount = $('#amount').val();
        var data = {
            'source': source,
            'destination': destination,
            'amount': amount
        }
        this.http_({
          method: 'POST',
          url: '/funding/maketransfer',
          data: JSON.stringify(data)
        })
        .then(
            function(response){
                console.log('post suceeded');
                console.log(response);
                if (response.data !== 'success') {
                    alert(response.data);
                } else {
                    alert('Transfer succeeded.')
                }
            },
            function(response){
                console.log('post failed');
                console.log(response);
            }
         );
      }
}

TransferComponentController.prototype.validate = function() {
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
      return isValid;
}