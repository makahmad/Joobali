AddPaymentController = function AddPaymentController($uibModal, $http, $scope) {
    /*
     * @input: programs
     */
    var self = this;
    self.invoices = [];
    self.children = [];
    self.newPayment = {};
    self.createButton = {};
    self.createSuccessLabel = {};
    self.createFailLabel = {};
    this.todayDate = new Date();


    $scope.paymentTypes = [{
      id: 'Cash',
      label: 'Cash'
    }, {
      id: 'Check',
      label: 'Check'
    }, {
      id: 'Other',
      label: 'Other'
    }];

    self.addPayment = function () {

      self.resolve.confirmAddComponentModal(self.newPayment);
    };



    self.updateProgramOptions = function(child_id) {
        if (!self.resolve.invoice) {
            $http({
                method: 'GET',
                url: '/invoice/listinvoicebychild',
                params: {'child_id': child_id}
            }).then(angular.bind(this, function successCallback(response) {
                // this callback will be called asynchronously
                // when the response is available
                this.invoices = [];
                angular.forEach(response.data, angular.bind(this, function(invoice) {
                    inv = JSON.parse(invoice);
                    if (inv.amount > 0) {
                        this.invoices.push(inv);
                    }
                }));
                //this.newPayment.program = this.programs[0];
            }), function errorCallback(response) {
                alert('Something is wrong here. Please refresh the page and try again');
            });
        } else {
            this.invoices = [];
            this.invoices.push(self.resolve.invoice);
            this.newPayment.invoice = self.resolve.invoice;
            this.newPayment.amount = self.resolve.invoice.amount;
        }
    }

    self.openPaymentDatePicker = function() {
        self.paymentDatePickerOpened = true;
    }

    self.resetModal = function() {
        self.dueDate = new Date();
        self.createSuccessLabel.show = false;
        self.createFailLabel.show = false;
    }

    self.$onInit = function() {
        self.resetModal();
    };

    self.closeModal = function() {
        self.dismiss({$value: 'cancel'});
    }

    $http({
        method: 'GET',
        url: '/child/list',
    }).then(angular.bind(this, function successCallback(response) {
        // this callback will be called asynchronously
        // when the response is available
        this.children = [];
        angular.forEach(response.data, angular.bind(this, function(child) {
            child_obj = JSON.parse(child);
            if (self.resolve.invoice) {
                if (self.resolve.invoice.child_id == child_obj.id) {
                    this.children.push(child_obj);
                }
            } else {
                this.children.push(child_obj);
            }
        }));
        this.newPayment.child = this.children[0];
        this.updateProgramOptions(this.newPayment.child['id'])
    }), function errorCallback(response) {
        // TODO(zilong): deal with error here
        console.log(response);
    });
}
