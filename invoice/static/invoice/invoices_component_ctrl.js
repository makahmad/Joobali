InvoicesComponentController = function($window, $http) {
    console.log('InvoicesComponentController running');
    this.window_ = $window;
    this.http_ = $http;
}

InvoicesComponentController.prototype.viewInvoice = function(clicked_invoice) {
    this.window_.location.href = '/invoice/viewinvoice?id=' + clicked_invoice.invoice_id;
}

InvoicesComponentController.prototype.buttonClicked = function(clicked_invoice) {
    if (this.isProvider == 'true') {
        var data = {
            'invoice_id': clicked_invoice.invoice_id
        }
        this.http_({
          method: 'POST',
          url: '/invoice/markpaid',
          data: JSON.stringify(data)
        })
        .then(
            function(response){
                console.log('post suceeded');
                if (response.data !== 'success') {
                    alert(response.data);
                } else {
                    alert('Marking invoice paid succeeded.')
                    clicked_invoice.paid = true;
                }
            },
            function(response){
                alert('Something is wrong. Please try again.');
            }
         );
    } else {
        if (this.fundings.length == 0) {
            $('#paymentSetupModal').modal('show');
        } else {
            $('#makePaymentModal').modal('show');
            for (i in this.invoices) {
                invoice = this.invoices[i];
                invoice.selected = false;
            }
            clicked_invoice.selected = true;
        }
    }
}

InvoicesComponentController.prototype.getButtonText = function() {
    if (this.isProvider == 'true') {
        return "Mark Paid";
    } else {
        return "Make Payment"
    }
}