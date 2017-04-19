AdjustInvoiceComponentController = function($location, $http) {
    console.log('AdjustInvoiceComponentController running');
    this.location_ = $location;
    this.http_ = $http;

    self = this
    self.closeModal = function() {
        self.dismiss({$value: 'cancel'});
    }
}

AdjustInvoiceComponentController.prototype.adjustInvoice = function() {
    var data = {
        'invoice_id': this.resolve.clickedInvoice.invoice_id,
        'amount': this.amount,
        'reason': this.reason,
    };
    console.log(this.invoices)
    console.log(this.getSelectedInvoice());
    console.log(data);
    self.http_.post('/invoice/adjustinvoice', data).then(function successCallback(response) {
        if (response.data == 'success') {
			location.reload();
        } else {
            alert('something is wrong');
        }
    }, function errorCallback(response) {
        alert('something is wrong');
    });
}

AdjustInvoiceComponentController.prototype.getSelectedInvoice = function() {
    for (i in this.invoices) {
        invoice = this.invoices[i];
        if (invoice.selected == true) {
            return invoice;
        }
    }
    return {};
}