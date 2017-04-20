AddInvoiceController = function AddInvoiceController($uibModalInstance, $http) {
    /*
     * @input: programs
     */
    var self = this;
    self.programs = [];
    self.children = [];
    self.newInvoice = {};
    self.createButton = {};
    self.createSuccessLabel = {};
    self.createFailLabel = {};


    self.createButton.click = function() {
        console.log("createButton is clicked");
        var data = {};
        if (self.newInvoice.child) {
            data = {
                'child_id': self.newInvoice.child.id,
                'program_id': self.newInvoice.program.id,
                'due_date': moment(self.newInvoice.due_date).format('MM/DD/YYYY'),
                'description': self.newInvoice.description,
                'amount': self.newInvoice.amount,
                'created_date': moment().format('MM/DD/YYYY'),
            };
        } else {
            all_ids = [];
            for (i in self.children) {
                all_ids.push(self.children[i].id);
            }
            data = {
                'all_children': all_ids,
                'due_date': moment(self.newInvoice.due_date).format('MM/DD/YYYY'),
                'description': self.newInvoice.description,
                'amount': self.newInvoice.amount,
                'created_date': moment().format('MM/DD/YYYY'),
            };
        }
        console.log(data);
        $http.post('/invoice/addinvoice', data).then(function successCallback(response) {
            if (response.data == 'success') {
                alert('Invoice created!');
                self.closeModal();
            } else {
                alert('something is wrong');
            }
        }, function errorCallback(response) {
            alert('something is wrong');
        });
    }

    self.updateProgramOptions = function(child_id) {
        if (this.newInvoice.child) {
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
                this.newInvoice.program = this.programs[0];
            }), function errorCallback(response) {
                alert('Something is wrong here. Please refresh the page and try again');
            });
        } else {
            this.programs = [];
        }
    }

    self.openDueDatePicker = function() {
        self.dueDatePickerOpened = true;
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
        this.newInvoice.child = this.children[0];
        this.updateProgramOptions(this.newInvoice.child['id'])
    }), function errorCallback(response) {
        // TODO(zilong): deal with error here
        console.log(response);
    });
}
