BillingComponentController = function($uibModal) {
    console.log('BillingComponentController running');
    var self = this;
    self.openAddFundingModal = function () {
       $('#addFundingIavModal').modal('show');
    };
};