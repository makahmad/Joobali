BillingComponentController = function($uibModal) {
    console.log('BillingComponentController running');
    var self = this;
    self.openAddFundingModal = function () {
       $uibModal.open({
           animation: true,
           component: 'addFundingIavComponent',
           backdrop  : 'static',
           keyboard  : false,
        });
    };
};