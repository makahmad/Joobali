var TIME_FORMAT =  'hh:mm A';

AddProgramFormComponentController = function($scope,$http) {
    console.log('AddProgramFormComponentController running');

    this._scope = $scope;
    var $ctrl = this;

    this.newProgram.startDate = moment().add(6, 'day').toDate();

    this.dayOfWeekDisplayOnly = moment(this.newProgram.startDate).format('dddd'); //change 0 to Sunday, 1 to Monday....
    this.dayOfMonthDisplayOnly = moment(this.newProgram.startDate).format('Do'); //change 1 to 1st, 2 to 2nd....
    this.startDateDisplayOnly = moment(this.newProgram.startDate).format('MM/DD/YYYY');

    this.openStartDatePicker = false;
    this.endDatePickerOpened = false;

    this.startDatePickerOptions = {
        minDate: moment().add(6, 'day')
    }

    this.endDatePickerOptions = {
        minDate: moment(this.newProgram.startDate).add(1, 'day'),
        dateDisabled: angular.bind(this, this.disabledEndDate)
    }


    $ctrl.openStartDatePicker = function () {
        this.startDatePickerOpened = true;
    };

    $ctrl.openEndDatePicker = function () {
        this.endDatePickerOpened = true;
    };


    $ctrl.$onInit = function () {
          	$http({
            method: 'GET',
            url: '/manageprogram/getdefaultlatefee'
        }).then(angular.bind(this, function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available

            this.newProgram.lateFee =JSON.parse(response.data);
            this.newProgram.registrationFee = 0;

        }), function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response);
        });
    };
};


AddProgramFormComponentController.prototype.indefiniteClicked = function() {
        if (this.newProgram.indefinite)
            this.newProgram.endDate = "";
}

// Disable invalid choices for billing end date
AddProgramFormComponentController.prototype.disabledEndDate = function(dateAndMode) {

    var result = false;
    if (dateAndMode.mode === 'day') {

        if (this.newProgram.billingFrequency != null) {

            //if weekly billing then end date must fall on the same day of the week
            if (this.newProgram.billingFrequency === 'Weekly') {
                result =  (moment(dateAndMode.date).format('MM/DD/YYYY')<=moment(this.newProgram.startDate).format('MM/DD/YYYY')
                || dateAndMode.date.getDay() != moment(this.newProgram.startDate).format('d'));
            }

            //if start date is after the 28th of the month, then end date must be last day of the next month
            else if (this.newProgram.billingFrequency === 'Monthly' && this.newProgram.lastDay) {
                var daysInStartDateMonth = moment(this.newProgram.startDate).daysInMonth();
                var lastDayInStartDateMonth = moment(this.newProgram.startDate).date(daysInStartDateMonth);
                var daysInEndDateMonth = moment(dateAndMode.date).daysInMonth();

                result = (moment(dateAndMode.date).format('MM/DD/YYYY')<=lastDayInStartDateMonth.format('MM/DD/YYYY')
                            || dateAndMode.date.getDate() != daysInEndDateMonth);
            }

            //if monthly billing and not last day of the month, then end date must fall on the same day of the month
            else if (this.newProgram.billingFrequency === 'Monthly') {
                result = (moment(dateAndMode.date).format('MM/DD/YYYY')<=moment(this.newProgram.startDate).format('MM/DD/YYYY')
                            || dateAndMode.date.getDate() != moment(this.newProgram.startDate).format('D'));
            }
        }
    }
    return result;

}

AddProgramFormComponentController.prototype.whenChangeStartDateOrFrequency = function() {
    var startDate = moment(this.newProgram.startDate);

    this.dayOfWeekDisplayOnly = startDate.format('dddd'); //change 0 to Sunday, 1 to Monday....
    this.dayOfMonthDisplayOnly = startDate.format('Do'); //change 1 to 1st, 2 to 2nd....
    this.startDateDisplayOnly = startDate.format('MM/DD/YYYY');

    if (startDate.format('D') > 28)
        this.newProgram.lastDay = true;
    else
        this.newProgram.lastDay = false;

    this.newProgram.endDate = null;

}