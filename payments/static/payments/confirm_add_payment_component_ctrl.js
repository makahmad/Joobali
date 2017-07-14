

ConfirmAddPaymentComponentController = function($http, $window, $location) {
    console.log('ConfirmAddPaymentComponentController running');
	this.http_ = $http;
	this.window_ = $window;
	this.program = {};
    this.location_ = $location;
    var self = this;

    this.newPayment = self.resolve.newPayment;

    self.paymentDateDisplay = moment(self.newPayment.payment_date).format('MM/DD/YYYY');

        self.cancel = function () {
          self.dismiss({$value: 'cancel'});
        };

};



ConfirmAddPaymentComponentController.prototype.addPayment = function() {
    var self = this;

    var invoice_id;
    if (self.newPayment.invoice!=null)
        invoice_id = self.newPayment.invoice.id;
    console.log("addPayment is clicked");
    var data = {
        'child_id': self.newPayment.child.id,
        'invoice_id': invoice_id,
        'payment_date': moment(self.newPayment.payment_date).format('MM/DD/YYYY'),
        'payer': self.newPayment.payer,
        'payment_type': self.newPayment.payment_type.id,
        'note': self.newPayment.note,
        'amount': self.newPayment.amount,
        'created_date': moment().format('MM/DD/YYYY'),
    };
    console.log(data);
    self.http_.post('/payments/addpayment', data).then(function successCallback(response) {
        if (response.data == 'success') {
			location.reload();
        } else {
            bootbox.alert('something is wrong');
        }
    }, function errorCallback(response) {
        bootbox.alert('something is wrong');
    });

};