InvoicesComponentController = function($location) {
    console.log('InvoicesComponentController running');
    this.location_ = $location;
}
InvoicesComponentController.prototype.showModal = function(invoice) {

    // TODO(rongjian): check if payment method was setup
    if (false) {
        $('#paymentSetupModal').modal('show');
    } else {
        $('#makePaymentModal').modal('show');
        for (i in this.invoices) {
            invoice = this.invoices[i];
            invoice.selected = false;
        }
        invoice.selected = true;
    }
}