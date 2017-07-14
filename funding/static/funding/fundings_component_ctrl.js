FundingsComponentController = function($location, $http) {
    console.log('FundingsComponentController running');
    this.location_ = $location;
    this.http_ = $http;
}

FundingsComponentController.prototype.removeFunding = function(funding) {

    bootbox.confirm({
        message: "Are you sure you want to remove funding source - " + funding.name,
        buttons: {
            confirm: {
                label: 'Yes',
                className: 'btn-success'
            },
            cancel: {
                label: 'No',
            }
        },
        callback: angular.bind(this, function(result) {
            if (result === true) {
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
                            bootbox.alert(response.data);
                        } else {
                            bootbox.alert('Removal succeeded.')
                            location.reload();
                        }
                    },
                    function(response){
                        console.log('post failed');
                        bootbox.alert(response);
                    }
                 );
            }
        })
    });
}