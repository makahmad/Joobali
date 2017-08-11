FundingsComponentController = function($location, $http, $uibModal) {
    console.log('FundingsComponentController running');
    this.location_ = $location;
    this.http_ = $http;
    this.uibModal_ = $uibModal;
}

FundingsComponentController.prototype.removeFunding = function(funding) {

    bootbox.confirm({
        message: "Are you sure you want to remove this funding source - " + funding.name + "?",
        buttons: {
            confirm: {
                label: 'Yes',
                className: 'btn btn-default btn-lg pull-right joobali'
            },
            cancel: {
                label: 'No',
				className: 'btn btn-default btn-lg pull-right'
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
                            bootbox.alert('Removal succeeded.', function() {
                                location.reload();
                            });
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

FundingsComponentController.prototype.verifyMicroDeposits = function(funding) {
    var modalInstance = this.uibModal_.open({
        animation: true,
        component: 'verifyMicroDepositsComponent',
            resolve: {
                funding: function () {
                   return funding;
                }
            }
        });
}