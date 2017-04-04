PaymentComponentController = function($uibModal) {
    var self = this;
    self.openAddPaymentModal = function() {
        console.log("Opening Add Payment Modal");
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: '/static/payments/add_payment_component_tmpl.html',
            controller: 'AddPaymentController',
            controllerAs: '$ctrl',
        });
    };
};