FundingsComponentController = function($location, $http) {
    console.log('FundingsComponentController running');
    this.location_ = $location;
    this.http_ = $http;
}

FundingsComponentController.prototype.removeFunding = function(funding) {
    if (confirm("Are you sure you want to remove funding source - " + funding.name)) {
        var data = {
            'funding_source_id': funding.id
        }
        this.http_({
          method: 'POST',
          url: '/funding/removefunding',
          data: JSON.stringify(data)
        })
        .then(
            function(response){
                console.log('post suceeded');
                console.log(response);
                if (response.data !== 'success') {
                    alert(response.data);
                } else {
                    alert('Removal succeeded.')
                    location.reload();
                }
            },
            function(response){
                console.log('post failed');
                alert(response);
            }
         );
    }
}