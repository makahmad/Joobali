InvoicesComponentController = function($window, $http, $uibModal) {
    console.log('InvoicesComponentController running');
    var self = this;
    self.sortType = 'due_date'; // set the default sort type
    self.sortReverse = true;  // set the default sort order
    self.searchTerm = '';     // set the default search/filter term
    self.openAdjustInvoiceModal = function(clicked_invoice) {
        console.log("Opening Adjust Invoice Modal");
        var modalInstance = $uibModal.open({
            animation: true,
            component: 'adjustInvoiceComponent',
            resolve: {
                clickedInvoice: function () {
                  return clicked_invoice;
                }
              }
            });
    };
    self.openAddPaymentModal = function(clicked_invoice) {
        console.log("Opening Add Payment Modal for 'Mark as Paid'");
        var modalInstance = $uibModal.open({
            animation: true,
            component: 'addPaymentComponent',
                resolve: {
                    confirmAddComponentModal: function () {
                       return self.confirmAddComponentModal;
                    },
                    invoice: function() {
                       return clicked_invoice;
                    }
              }
            });
    };


    self.confirmAddComponentModal = function (newPayment) {
        console.log("Opening confirmAddComponentModal");
        var modalInstance = $uibModal.open({
            animation: true,
            component: 'confirmAddPaymentComponent',
            resolve: {
            newPayment: function () {
              return newPayment;
            }
            }
        });
    };

    self.buttonClicked = function(clicked_invoice) {
        if (this.isProvider == 'true') {
            this.openAddPaymentModal(clicked_invoice);
        } else {

            if (clicked_invoice.paid == false && clicked_invoice.processing == false) {
                // Make Payment
                if (this.fundings.length == 0) {
                    var modalInstance = $uibModal.open({
                        animation: true,
                        component: 'paymentSetupComponent',
                    });
                } else {
                    $('#makePaymentModal').modal('show');
                    for (i in this.invoices) {
                        invoice = this.invoices[i];
                        invoice.selected = false;
                    }
                    clicked_invoice.selected = true;
                }
            } else if (clicked_invoice.processing == true && clicked_invoice.paid == false) {
                // Cancel Payment
                bootbox.confirm({
                    message: "Do you really want to cancel the payment?",
                    buttons: {
                        confirm: {
                            label: 'Yes',
                            className: 'btn-success'
                        },
                        cancel: {
                            label: 'No',
                        }
                    },
                    callback: angular.bind(this, function(result) {
                        if (result === true) {
                            var data = {
                                'invoice_id': clicked_invoice.invoice_id
                            }
                            this.http_({
                              method: 'POST',
                              url: '/invoice/cancelpayment',
                              data: JSON.stringify(data)
                            })
                            .then(
                                function(response){
                                    if (response.data !== 'success') {
                                        bootbox.alert(response.data);
                                    } else {
                                        bootbox.alert('Payment cancelled successfully.')
                                        location.reload();
                                    }
                                },
                                function(response){
                                    bootbox.alert('Payment cancellation failed. Please contact us for this issue.');
                                }
                             );
                        }
                    })
                });
            }
        }
    }
    this.window_ = $window;
    this.http_ = $http;
}

InvoicesComponentController.prototype.viewInvoice = function(clicked_invoice) {
    this.window_.location.href = '/invoice/viewinvoice?id=' + clicked_invoice.invoice_id;
}

InvoicesComponentController.prototype.adjustButtonClicked = function(clicked_invoice) {
    if (this.isProvider == 'true') {
        this.openAdjustInvoiceModal(clicked_invoice);
    }
}

InvoicesComponentController.prototype.cancelAutopayClicked = function(clicked_invoice) {
        bootbox.confirm({
            message: "Do you really want to cancel the autopay?",
            buttons: {
                confirm: {
                    label: 'Yes',
                    className: 'btn-success'
                },
                cancel: {
                    label: 'No',
                }
            },
            callback: angular.bind(this, function(result) {
                if (result === true) {
                    var data = {
                        'invoice_id': clicked_invoice.invoice_id
                    }
                    this.http_({
                      method: 'POST',
                      url: '/invoice/cancelautopay',
                      data: JSON.stringify(data)
                    })
                    .then(
                        function(response){
                            if (response.data !== 'success') {
                                bootbox.alert(response.data);
                            } else {
                                bootbox.alert('Autopay cancelled successfully.')
                                location.reload();
                            }
                        },
                        function(response){
                            bootbox.alert('Autopay cancellation failed. Please contact us for this issue.');
                        }
                     );
                }
            })
        });
}

InvoicesComponentController.prototype.getButtonText = function(invoice) {
    if (this.isProvider == 'true') {
        return "Mark Paid";
    } else {
        if (!invoice.paid && !invoice.processing) {
            return "Make Payment";
        } else if (invoice.processing && !invoice.paid) {
            return "Cancel Payment";
        }
    }
}