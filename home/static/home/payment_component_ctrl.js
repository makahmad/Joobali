PaymentComponentController = function($uibModal) {
    var self = this;
    self.openAddInvoiceModal = function() {
        console.log("Opening Add Invoice Modal");
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: '/static/payments/add_invoice_component_tmpl.html',
            controller: 'AddInvoiceController',
            controllerAs: '$ctrl',
        });
    };
};