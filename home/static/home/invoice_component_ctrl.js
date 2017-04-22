InvoiceComponentController = function($uibModal) {
    var self = this;
    self.openAddInvoiceModal = function() {
        console.log("Opening Add Invoice Modal");
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: '/static/invoice/add_invoice_component_tmpl.html',
            controller: 'AddInvoiceController',
            controllerAs: '$ctrl',
        });
    };

    self.openInvoiceSettingsModal = function() {
        console.log("Opening  Invoice Settings Modal");
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: '/static/invoice/invoice_settings_component_tmpl.html',
            controller: 'InvoiceSettingsController',
            controllerAs: '$ctrl',
        });
    };

};