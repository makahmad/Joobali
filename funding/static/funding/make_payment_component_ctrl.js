MakePaymentComponentController = function($location, $http) {
    console.log('MakePaymentComponentController running');
    this.location_ = $location;
    this.http_ = $http;
    self = this;
    $('#makePaymentModal').on('hidden.bs.modal', function () {
        self.autopayOptIn = false;
        if (self.showPaymentSuccessAlert) {
            location.reload();
        }
    })


    this.showPaymentSuccessAlert = false;
    this.showPaymentFailureAlert = false;
    this.showAutopaySuccessAlert = false;
    this.showAutopayFailureAlert = false;
    this.paymentFailureMessage = '';
    this.autopaySuccessMessage = '';

    this.disableButton = false;
}


MakePaymentComponentController.prototype.getSelectedInvoice = function() {
    for (i in this.invoices) {
        invoice = this.invoices[i];
        if (invoice.selected == true) {
            return invoice;
        }
    }
    return {};
}

MakePaymentComponentController.prototype.makePayment = function() {

      if (this.validate()) {
        this.disableButton = true;
        var source = $('#source :selected').val();
        var selected_invoice = this.getSelectedInvoice();
        var destination = selected_invoice.provider_customer_id;
        var amount = selected_invoice.amount;
        var data = {
            'source': source,
            'destination': destination,
            'amount': amount,
            'invoice_id': selected_invoice.invoice_id
        }
        self = this;

        this.http_({
          method: 'POST',
          url: '/funding/maketransfer',
          data: JSON.stringify(data)
        })
        .then(
            angular.bind(this, function(response){
                console.log('post suceeded');
                console.log(response);
                if (response.data !== 'success') {
                    this.disableButton = false;
                    this.paymentFailureMessage = response.data;
                    this.showPaymentFailureAlert = true;
                } else {
                    this.showPaymentSuccessAlert = true;
                }
            }),
            angular.bind(this, function(response){
                this.disableButton = false;
                console.log('post failed: ' + response.data);
                this.paymentFailureMessage = response.data;
                this.showPaymentFailureAlert = true;
            })
         );

         if (this.autopayOptIn) {
            this.setupAutopay();
         }
      }
}

MakePaymentComponentController.prototype.autopayable = function() {
    var selected_invoice = this.getSelectedInvoice();
    return selected_invoice.is_recurring;
}

MakePaymentComponentController.prototype.setupAutopay = function() {
      if (this.validate()) {
        var source = $('#source :selected').val();
        var selected_invoice = this.getSelectedInvoice();
        var data = {
            'source': source,
            'invoice_id': selected_invoice.invoice_id
        }
        this.http_({
          method: 'POST',
          url: '/invoice/setupautopay',
          data: JSON.stringify(data)
        })
        .then(
            angular.bind(this, function(response){
                console.log('post suceeded');
                console.log(response);
                if (response.data !== 'success') {
                    this.autopayFailureMessage = response.data;
                    this.showAutopayFailureAlert = true;
                } else {
                    this.showAutopaySuccessAlert = true;
                }
            }),
            angular.bind(this, function(response){
                console.log('post failed: ' + response.data);
                this.autopayFailureMessage = response.data;
                this.showAutopayFailureAlert = true;
            })
         );
      }
}

MakePaymentComponentController.prototype.validate = function() {
      var curContent = $("#transferForm");

      var curInputs = curContent.find("input"),
      isValid = true;

          $(".form-group").removeClass("has-error");
          for(var i=0; i< curInputs.length; i++){
              if (!curInputs[i].validity.valid){
                  isValid = false;
                  $(curInputs[i]).closest(".form-group").addClass("has-error");
              }
          }
      return isValid;
}