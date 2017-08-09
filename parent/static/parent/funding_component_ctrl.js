FundingComponentController = function($uibModal) {
    console.log('FundingComponentController running');
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