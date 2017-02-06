MakePaymentComponentController = function($location, $http) {
    console.log('MakePaymentComponentController running');
    this.location_ = $location;
    this.http_ = $http;

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
        this.http_({
          method: 'POST',
          url: '/funding/maketransfer',
          data: JSON.stringify(data)
        })
        .then(
            function(response){
                console.log('post suceeded');
                console.log(response);
                if (response.data !== 'success') {
                    alert(response.data);
                } else {
                    alert('Transfer succeeded.')
                }
            },
            function(response){
                console.log('post failed');
                console.log(response);
            }
         );
      }
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
            function(response){
                console.log('post suceeded');
                console.log(response);
                if (response.data !== 'success') {
                    alert(response.data);
                } else {
                    alert('Autopay setup succeeded.')
                }
            },
            function(response){
                console.log('post failed');
                console.log(response);
            }
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