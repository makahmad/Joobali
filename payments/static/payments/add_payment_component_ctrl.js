AddPaymentController = function AddPaymentController($uibModalInstance, $http, $scope) {
    /*
     * @input: programs
     */
    var self = this;
    self.programs = [];
    self.children = [];
    self.newPayment = {};
    self.createButton = {};
    self.createSuccessLabel = {};
    self.createFailLabel = {};

    $scope.paymentTypes = [{
      id: 'Cash',
      label: 'Cash'
    }, {
      id: 'Check',
      label: 'Check'
    }];

    self.createButton.click = function() {
        console.log("createButton is clicked");
        var data = {
            'child_id': self.newPayment.child.id,
           // 'program_id': self.newPayment.program.id,
            'payment_date': moment(self.newPayment.payment_date).format('MM/DD/YYYY'),
            'payer': self.newPayment.payer,
            'payment_type': self.newPayment.payment_type.id,
            'amount': self.newPayment.amount,
            'created_date': moment().format('MM/DD/YYYY'),
        };
        console.log(data);
        $http.post('/payments/addpayment', data).then(function successCallback(response) {
            if (response.data == 'success') {
                alert('Payment created!');
                self.closeModal();
            } else {
                alert('something is wrong');
            }
        }, function errorCallback(response) {
            alert('something is wrong');
        });
    }

    self.updateProgramOptions = function(child_id) {
        $http({
            method: 'GET',
            url: '/manageprogram/listprogrambychild',
            params: {'child_id': child_id}
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available
            this.programs = [];
            angular.forEach(response.data, angular.bind(this, function(program) {
                this.programs.push(JSON.parse(program));
            }));
            this.newPayment.program = this.programs[0];
        }), function errorCallback(response) {
            alert('Something is wrong here. Please refresh the page and try again');
        });
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
        $uibModalInstance.close();
    }

    $http({
        method: 'GET',
        url: '/child/list',
    }).then(angular.bind(this, function successCallback(response) {
        // this callback will be called asynchronously
        // when the response is available
        this.children = [];
        angular.forEach(response.data, angular.bind(this, function(child) {
            this.children.push(JSON.parse(child));
        }));
        console.log(this.children);
        this.newPayment.child = this.children[0];
        this.updateProgramOptions(this.newPayment.child['id'])
    }), function errorCallback(response) {
        // TODO(zilong): deal with error here
        console.log(response);
    });
}
