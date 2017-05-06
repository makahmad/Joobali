InvoicesComponentController = function($window, $http, $uibModal) {
    console.log('InvoicesComponentController running');
    var self = this;
    self.sortType = 'child'; // set the default sort type
    self.sortReverse = false;  // set the default sort order
    self.searchTerm = '';     // set the default search/filter term
    self.openAdjustInvoiceModal = function(clicked_invoice) {
        console.log("Opening Adjust Invoice Modal");
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: '/static/invoice/adjust_invoice_component_tmpl.html',
            controller: 'AdjustInvoiceComponentController',
            controllerAs: '$ctrl',
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
    this.window_ = $window;
    this.http_ = $http;
}

InvoicesComponentController.prototype.viewInvoice = function(clicked_invoice) {
    this.window_.location.href = '/invoice/viewinvoice?id=' + clicked_invoice.invoice_id;
}

InvoicesComponentController.prototype.buttonClicked = function(clicked_invoice) {
    if (this.isProvider == 'true') {
        this.openAddPaymentModal(clicked_invoice);
//        var data = {
//            'invoice_id': clicked_invoice.invoice_id
//        }
//        this.http_({
//          method: 'POST',
//          url: '/invoice/markpaid',
//          data: JSON.stringify(data)
//        })
//        .then(
//            function(response){
//                console.log('post suceeded');
//                if (response.data !== 'success') {
//                    alert(response.data);
//                } else {
//                    alert('Marking invoice paid succeeded.')
//                    clicked_invoice.paid = true;
//                }
//            },
//            function(response){
//                alert('Something is wrong. Please try again.');
//            }
//         );
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

InvoicesComponentController.prototype.adjustButtonClicked = function(clicked_invoice) {
    if (this.isProvider == 'true') {
        this.openAdjustInvoiceModal(clicked_invoice);
    }
}

InvoicesComponentController.prototype.getButtonText = function() {
    if (this.isProvider == 'true') {
        return "Mark Paid";
    } else {
        return "Make Payment"
    }
}