VerifyMicroDepositsComponentController = function($http) {
    console.log('VerifyMicroDepositsComponentController running');
    this.http_ = $http;
    self = this

    this.showVerifySuccessAlert = false;
    this.showVerifyFailureAlert = false;
    this.verifyFailureMessage = '';

    this.disableButton = false;
    this.showCancel = false;

    self.cancel = function() {
        self.dismiss({$value: 'cancel'});
        if (this.showCancel == true) {
          location.reload();
        }
    }
    self.verify = function() {
      funding = self.resolve.funding;
      data = {
        'funding_url': funding.url,
        'first_amount': self.firstAmount,
        'second_amount': self.secondAmount,
      }
      this.disableButton = true;
        this.http_({
          method: 'POST',
          url: '/funding/verifymicrodeposits',
          data: JSON.stringify(data)
        })
        .then(
            angular.bind(this, function(response){
                console.log('post suceeded');
                console.log(response);
                if (response.data !== 'success') {
                    this.disableButton = false;
                    this.verifyFailureMessage = response.data;
                    this.showVerifyFailureAlert = true;
                    this.showVerifySuccessAlert = false;
                } else {
                    this.showCancel = true;
                    this.showVerifySuccessAlert = true;
                    this.showVerifyFailureAlert = false;
                }
            }),
            angular.bind(this, function(response){
                this.disableButton = false;
                console.log('post failed: ' + response.data);
                this.verifyFailureMessage = response.data;
                this.showVerifyFailureAlert = true;
                this.showVerifySuccessAlert = false;
            })
         );
    }
};