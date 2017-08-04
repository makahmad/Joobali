AdjustInvoiceComponentController = function($uibModal, $location, $http) {
    console.log('AdjustInvoiceComponentController running');
    this.location_ = $location;
    this.http_ = $http;

    self = this;
    self.closeModal = function() {
        self.dismiss({$value: 'cancel'});
    }

    self.adjustInvoice = function() {
        var data = {
            'invoice_id': this.resolve.clickedInvoice.invoice_id,
            'amount': this.amount,
            'reason': this.reason,
        };
        this.http_.post('/invoice/adjustinvoice', data).then(function successCallback(response) {
            if (response.data == 'success') {
                self.closeModal()
                location.reload();
            } else {
                bootbox.alert(response.data);
            }
        }, function errorCallback(response) {
            bootbox.alert('something is wrong: %s' % response.data);
        });
    }

    self.getSelectedInvoice = function() {
        for (i in this.invoices) {
            invoice = this.invoices[i];
            if (invoice.selected == true) {
                return invoice;
            }
        }
        return {};
    }
}
