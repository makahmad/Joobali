PaymentSetupComponentController = function($http) {
    console.log('PaymentSetupComponentController running');
    this.http_ = $http;
    self = this
    $http({
          method: 'GET',
          url: '/funding/getiavtoken'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            this.iavToken = response.data;
            console.log('IAV token fetched: ' + this.iavToken);
            dwolla.configure(window.location.hostname.indexOf('joobali-prod') != -1 ? 'prod' : 'sandbox');
            dwolla.iav.start(this.iavToken, {container: 'paymentSetupIavContainer'}, angular.bind(this, function(err, res) {
                console.log('Error: ' + JSON.stringify(err) + ' -- Response: ' + JSON.stringify(res));
                if (!err) {
                    // Funding IAV successful
                    //$('#initSetupNextButton').show();
                    location.reload();
                }
            }));
        }), function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response);
        });

    self.cancel = function() {
        self.dismiss({$value: 'cancel'});
    }
};