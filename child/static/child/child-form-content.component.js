ChildFormContentController = function ChildFormContentController($http, EnrollmentDateChecker) {
    this.http_ = $http;
    this.dateOfBirthPickerOpened = false;
    this.startDatePickerOpened = false;
    this.endDatePickerOpened = false;
    this.readOnly = false;
    this.todayDate = new Date();
    this.dateFormat = 'MM/DD/YYYY';
    this.showSaveButton = true;
    this.disableSaveButton = false;
    this.isAddNewParent = (this.emails.length == 0);
    this.newChildEnrollmentInfo = {"program":{}};
    this.startDate = moment().add(6, 'day');
    this.newChildEnrollmentInfo.start_date = this.startDate.toDate();

	this.newChildEnrollmentInfo.program = { "startDate": this.startDate,
	                    "endDate": null,
                        "programName":null,
                        "registrationFee":0,
                        "lateFee":0,
	                    "billingFrequency": "Monthly",
	                    "weeklyBillDay": this.startDate.format('dddd'),
	                    "monthlyBillDay": this.startDate.format('D'),
	                    "indefinite": false,
	                    "lastDay": false,
                        "showLastDayCheckbox":false};

	this.whenChangeStartDateOrFrequency();
    //
    // if ( this.newChildEnrollmentInfo.program.startDate.format('D') > 28 ) {
    //     // this.newChildEnrollmentInfo.program.lastDay = true;
    //     this.newChildEnrollmentInfo.program.showLastDayCheckbox = true;
    // }


    this.dayOfWeekDisplayOnly = moment(this.newChildEnrollmentInfo.program.startDate).format('dddd'); //change 0 to Sunday, 1 to Monday....
    this.dayOfMonthDisplayOnly = moment(this.newChildEnrollmentInfo.program.startDate).format('Do'); //change 1 to 1st, 2 to 2nd....
    this.startDateDisplayOnly = moment(this.newChildEnrollmentInfo.program.startDate).format('MM/DD/YYYY');

    // this.openStartDatePicker = false;
    // this.endDatePickerOpened = false;


    // this.disableLastDayCheckbox = false;
    //
    //
    // this.startDatePickerOptions = {
    //     minDate: moment().add(6, 'day')
    // }
    //
    // this.endDatePickerOptions = {
    //     minDate: moment(this.newProgram.startDate).add(1, 'day'),
    //     dateDisabled: angular.bind(this, this.disabledEndDate)
    // }
    //
    //
    // $ctrl.openStartDatePicker = function () {
    //     this.startDatePickerOpened = true;
    // };
    //
    // $ctrl.openEndDatePicker = function () {
    //     this.endDatePickerOpened = true;
    // };




    // this.newChildEnrollmentInfo.start_date = this.todayDate;
    // this.newChildEnrollmentInfo.program = {};
    // this.newChildEnrollmentInfo.program.startDate = this.todayDate;
    // this.newChildEnrollmentInfo.program.weeklyBillDay = "Friday";
    // this.newChildEnrollmentInfo.program.monthlyBillDay = 1;




    this.newChildEnrollmentInfo.error = {};
    this.enrollmentDateChecker_ = EnrollmentDateChecker;


    this.enrollmentStatus = '';
    this.enrollmentDatePickerOptions = { // for start date
        minDate:  this.startDate,
        dateDisabled: angular.bind(this, this.enrollmentDisabledDate),
        showWeeks: false
    }

    this.enrollmentEndDatePickerOptions = {
        minDate: this.startDate,
        dateDisabled: angular.bind(this, this.enrollmentDisabledEndDate)
    }


    this.paymentTypes = [{
      id: 'Cash',
      label: 'Cash'
    }, {
      id: 'Check',
      label: 'Check'
    }, {
      id: 'Other',
      label: 'Other'
    }];
}



ChildFormContentController.prototype.whenChangeStartDateOrFrequency = function () {


    if (this.newChildEnrollmentInfo.program && this.newChildEnrollmentInfo.program.programName) {

        if (this.newChildEnrollmentInfo.program.endDate) {
            this.newChildEnrollmentInfo.end_date = moment(this.newChildEnrollmentInfo.program.endDate).toDate();
        } else {
            this.newChildEnrollmentInfo.end_date = "";
        }

    } else {
        var startDate = moment(this.newChildEnrollmentInfo.start_date);
        this.dayOfWeekDisplayOnly = startDate.format('dddd'); //change 0 to Sunday, 1 to Monday....
        this.dayOfMonthDisplayOnly = startDate.format('Do'); //change 1 to 1st, 2 to 2nd....
        this.startDateDisplayOnly = startDate.format('MM/DD/YYYY');
        this.disableLastDayCheckbox = false;


        this.newChildEnrollmentInfo.program.weeklyBillDay = startDate.format('dddd');
        this.newChildEnrollmentInfo.program.monthlyBillDay = startDate.format('D');


        //if day of start date is the last day of the month, show Last Day checkbox
        if (startDate.format('D') == startDate.daysInMonth()) {
            this.newChildEnrollmentInfo.program.showLastDayCheckbox = true;

            //if day of last day is the 31st, then check the Last Day checbkox and make it read only
            if (startDate.format('D') == 31) {
                this.newChildEnrollmentInfo.program.lastDay = true;
                this.disableLastDayCheckbox = true;
            }
        }
        else {
            this.newChildEnrollmentInfo.program.lastDay = false;
            this.newChildEnrollmentInfo.program.showLastDayCheckbox = false;
        }

        this.newChildEnrollmentInfo.end_date = null;
        this.newChildEnrollmentInfo.program.endDate = null;


    }
        this.whenChangeEndDate();
}

ChildFormContentController.prototype.whenSelectedProgramChange = function () {

    if (this.newChildEnrollmentInfo.program && this.newChildEnrollmentInfo.program.programName) {
        this.newChildEnrollmentInfo.start_date = moment(this.newChildEnrollmentInfo.program.startDate).toDate();
        if (this.newChildEnrollmentInfo.program.endDate) {
            this.newChildEnrollmentInfo.end_date = moment(this.newChildEnrollmentInfo.program.endDate).toDate();
        } else {
            this.newChildEnrollmentInfo.end_date = "";
        }
        this.newChildEnrollmentInfo.fee = this.newChildEnrollmentInfo.program.fee;
    } else {

        // this.newChildEnrollmentInfo.start_date = this.todayDate;
        this.startDate = moment().add(6, 'day');
        this.newChildEnrollmentInfo.start_date = this.startDate.toDate();
        this.newChildEnrollmentInfo.fee = null;

        this.newChildEnrollmentInfo.program = { "startDate": this.startDate,
                    "endDate": null,
                     "programName":null,
                                    "registrationFee":0,
                        "lateFee":0,
                    "billingFrequency": "Monthly",
                    "weeklyBillDay": this.startDate.format('dddd'),
                    "monthlyBillDay": this.startDate.format('D'),
                    "indefinite": false,
                    "lastDay": false,
                    "showLastDayCheckbox":false};


    }
    this.whenChangeStartDateOrFrequency();
}

ChildFormContentController.prototype.whenChangeStartDate = function() {
        if (this.newChildEnrollmentInfo.program && this.newChildEnrollmentInfo.program.endDate) {
            this.newChildEnrollmentInfo.end_date = moment(this.newChildEnrollmentInfo.program.endDate).toDate();
        } else {
            this.newChildEnrollmentInfo.end_date = null;
        }

    // if (this.newChildEnrollmentInfo.program.programName) {
    //     if (this.newChildEnrollmentInfo.program && this.newChildEnrollmentInfo.program.endDate) {
    //         this.newChildEnrollmentInfo.end_date = moment(this.newChildEnrollmentInfo.program.endDate).toDate();
    //     } else {
    //         this.newChildEnrollmentInfo.end_date = null;
    //     }
    // } else {
    //               console.log("in whenChangeStartDate");
    //
    // }


}


// Disable invalid choices for billing end date
ChildFormContentController.prototype.enrollmentDisabledEndDate = function(dateAndMode) {

    if (this.newChildEnrollmentInfo.program && this.newChildEnrollmentInfo.program.programName) {
        return this.enrollmentDateChecker_.isEnrollmentEndDateDisabled(
                dateAndMode,
                this.newChildEnrollmentInfo.program,
                this.newChildEnrollmentInfo.start_date);
    } else {
        var result = false;
        if (dateAndMode.mode === 'day') {

            if (this.newChildEnrollmentInfo.program.billingFrequency != null) {

                //if weekly billing then end date must fall on the same day of the week
                if (this.newChildEnrollmentInfo.program.billingFrequency === 'Weekly') {
                    result =  (dateAndMode.date<=this.newChildEnrollmentInfo.start_date
                    || dateAndMode.date.getDay() != moment(this.newChildEnrollmentInfo.start_date).format('d')
                    );
                }

                //if start date is after the 28th of the month, then end date must be last day of the next month
                else if (this.newChildEnrollmentInfo.program.billingFrequency === 'Monthly' && this.newChildEnrollmentInfo.program.lastDay) {
                    var daysInStartDateMonth = moment(this.newChildEnrollmentInfo.start_date).daysInMonth();
                    var lastDayInStartDateMonth = moment(this.newChildEnrollmentInfo.start_date).date(daysInStartDateMonth);
                    var daysInEndDateMonth = moment(dateAndMode.date).daysInMonth();

                    result = (dateAndMode.date<=lastDayInStartDateMonth
                                || dateAndMode.date.getDate() != daysInEndDateMonth);
                }

                //if monthly billing and not last day of the month, then end date must fall on the same day of the month
                else if (this.newChildEnrollmentInfo.program.billingFrequency === 'Monthly') {
                    result = (dateAndMode.date<=this.newChildEnrollmentInfo.start_date
                                || dateAndMode.date.getDate() != moment(this.newChildEnrollmentInfo.start_date).format('D'));
                }
            }
        }
        return result;
    }

}

ChildFormContentController.prototype.enrollmentDisabledDate = function(dateAndMode) {

    if (this.newChildEnrollmentInfo.program && this.newChildEnrollmentInfo.program.programName) {

        return this.enrollmentDateChecker_.isEnrollmentDateDisabled(
                dateAndMode,
                this.newChildEnrollmentInfo.program);
    } else {

        return false;

    }

}


ChildFormContentController.prototype.whenChangeEndDate = function() {

    if(this.newChildEnrollmentInfo.program.billingFrequency=='Monthly' && this.newChildEnrollmentInfo.program.lastDay)
        this.programInfoDisplay = 'We will automatically collect fees on the last day of '+
        'each month starting '+this.startDateDisplayOnly;
    else if(this.newChildEnrollmentInfo.program.billingFrequency=='Monthly' && !this.newChildEnrollmentInfo.program.lastDay)
        this.programInfoDisplay = 'We will automatically collect fees on the '+this.dayOfMonthDisplayOnly+
                              ' day of each month starting '+this.startDateDisplayOnly;
    else if(this.newChildEnrollmentInfo.program.billingFrequency=='Weekly')
        this.programInfoDisplay = 'We will automatically collect fees weekly on '+this.dayOfWeekDisplayOnly+'s'+
                              ' starting '+this.startDateDisplayOnly;

    if(this.newChildEnrollmentInfo.end_date)
        this.programInfoDisplay += ' and ending on '+moment(this.newChildEnrollmentInfo.end_date).format('MM/DD/YYYY')+'.';
    else
        this.programInfoDisplay += ' indefinitely.'
}

ChildFormContentController.prototype.whenChangeLastDay = function() {

    if (this.newChildEnrollmentInfo.start_date && this.newChildEnrollmentInfo.end_date)
    {
        var endDate = moment(this.newChildEnrollmentInfo.end_date);
        var startDate = moment(this.newChildEnrollmentInfo.start_date);


        //if last day is checked, and end date is not last day of a month, clear end date
        if (this.newChildEnrollmentInfo.program.lastDay && endDate.format('D') != endDate.daysInMonth())
            this.newChildEnrollmentInfo.end_date = null;

        //if last day is unchecked, and end date is not the same day of a start month, clear end date
        if (!this.newChildEnrollmentInfo.program.lastDay && startDate.format('D')!=endDate.format('D'))
            this.newChildEnrollmentInfo.end_date = null;

    }

    this.whenChangeEndDate();

}


ChildFormContentController.prototype.openDateOfBirthPicker = function() {
    this.dateOfBirthPickerOpened = ! this.dateOfBirthPickerOpened;
};

ChildFormContentController.prototype.openStartDatePicker = function() {
    this.startDatePickerOpened = ! this.startDatePickerOpened;
};

ChildFormContentController.prototype.openEndDatePicker = function() {
    this.endDatePickerOpened = ! this.endDatePickerOpened;
};

ChildFormContentController.prototype.openPaymentDatePicker = function() {
    this.paymentDatePickerOpened = true;
}

ChildFormContentController.prototype.save = function() {
    isValid = true;
    angular.forEach(addChildForm, angular.bind(this, function(value, key) {
        if (value.tagName == 'INPUT' || value.tagName == 'SELECT'){
            if(angular.element(value).hasClass('ng-invalid')) {
                this.newChildEnrollmentInfo.error[value.id] = true;
                isValid = false;
            } else {
                this.newChildEnrollmentInfo.error[value.id] = false;
            }
        }
    }));
    if (!isValid) {
        return;
    }

    var submittingForm = angular.copy(this.newChildEnrollmentInfo);
    if (submittingForm.child_date_of_birth) {
        submittingForm.child_date_of_birth = moment(submittingForm.child_date_of_birth).format("MM/DD/YYYY");
    } else {
        submittingForm.child_date_of_birth = '';
    }
    console.log(submittingForm.child_date_of_birth);
    submittingForm.start_date = moment(submittingForm.start_date).format("MM/DD/YYYY");
    submittingForm.end_date = submittingForm.end_date ? moment(submittingForm.end_date).format("MM/DD/YYYY") : "";

    if (submittingForm.payment_date) {
        submittingForm.payment_date = moment(submittingForm.payment_date).format("MM/DD/YYYY");
    } else {
        submittingForm.payment_date = '';
    }
    if (submittingForm.payment_type) {
        submittingForm.payment_type = submittingForm.payment_type.id;
    }

    this.disableSaveButton = true;
    this.http_.post('/child/add', submittingForm).then(angular.bind(this, function successCallback(response) {
        if (response.data.status == 'success') {
            this.enrollmentStatus = 'success';
            this.showSaveButton = false;
            this.onSave({'isSaved': true});
            this.readOnly = true;
        } else {
            this.enrollmentStatus = 'failure';
            this.onSave({'isSaved': false});
            this.readOnly = false;
            this.disableSaveButton = false;
            this.enrollmentFailureReason = response.data;
        }
    }), angular.bind(this, function errorCallback(response) {
        this.enrollmentStatus = 'failure';
        this.onSave({'isSaved': false});
        this.readOnly = false;
        this.enrollmentFailureReason = response.data;
        this.disableSaveButton = false;
    }));
}

ChildFormContentController.prototype.newParentToggle = function() {
    this.isAddNewParent = !this.isAddNewParent;
}

ChildFormContentController.prototype.cancel = function() {
    this.onClose();
}