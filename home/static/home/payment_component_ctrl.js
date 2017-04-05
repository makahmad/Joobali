PaymentComponentController = function($uibModal) {
    var self = this;

    self.openAddPaymentModal = function() {
        console.log("Opening Add Payment Modal");
        var modalInstance = $uibModal.open({
            animation: true,
            component: 'addPaymentComponent',
               resolve: {
                confirmAddComponentModal: function () {
                  return self.confirmAddComponentModal;
                }

              }
            });
    };


      self.confirmAddComponentModal = function (newPayment) {
        console.log("Opening confirmAddComponentModal");


      console.log(newPayment);
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
};