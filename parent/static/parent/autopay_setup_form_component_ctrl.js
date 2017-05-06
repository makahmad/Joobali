AutopaySetupFormComponentController = function($http) {
    console.log('AutopaySetupFormComponentController running');
    this.http_ = $http;

};

AutopaySetupFormComponentController.prototype.updateSelectedBankName = function() {
    if (this.data.bankAccountId) {
        angular.forEach(this.data.bankAccounts, angular.bind(this, function(account) {
            if (account.id == this.data.bankAccountId) {
                this.data.bankAccountName = account.name;
            }
        }));
    }
    console.log(this.data.bankAccountId);
    console.log(this.data.bankAccountName);
};