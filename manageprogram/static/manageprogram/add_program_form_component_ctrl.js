var TIME_FORMAT =  'hh:mm A';

AddProgramFormComponentController = function($scope,$http) {
    console.log('AddProgramFormComponentController running');

	this.initializeTimePickers();
    this._scope = $scope;
    var $ctrl = this;

    var startDate = new Date( Date.parse(this.newProgram.startDate) );
    this.days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    this.dayOfWeekDisplayOnly = this.days[ startDate.getDay() ]; //change 0 to Sunday, 1 to Monday....
    this.dayOfMonthDisplayOnly = ordinal_suffix_of(startDate.getDate()); //change 1 to 1st, 2 to 2nd....

//    $ctrl.weeklyBillDays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
//
//    $ctrl.monthlyBillDays = [];
//    for(var i=1;i<=28;i++)
//        $ctrl.monthlyBillDays.push(i);
//     $ctrl.monthlyBillDays.push("Last Day");

    $ctrl.indefiniteClicked = function () {
        if (this.newProgram.indefinite)
            this.newProgram.endDate = "";
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

AddProgramFormComponentController.prototype.initializeTimePickers = function() {
    $('#startDate').datetimepicker({
        format: 'MM/DD/YYYY',
        minDate: moment().millisecond(0).second(0).minute(0).hour(0), // BUG source: https://github.com/Eonasdan/bootstrap-datetimepicker/issues/1302
    })
    .on('dp.change', angular.bind(this, function(e) {
        console.log('fired1');
        $('#endDate').data('DateTimePicker').minDate(e.date);
        this.newProgram.startDate = $('#startDate').val();

        var startDate = new Date( Date.parse(this.newProgram.startDate) );

        this.dayOfMonthDisplayOnly = ordinal_suffix_of(startDate.getDate()); //change 1 to 1st, 2 to 2nd....
        this.dayOfWeekDisplayOnly = this.days[ startDate.getDay() ]; //change 0 to Sunday, 1 to Monday....

        if (startDate.getDate() > 28)
            this.newProgram.lastDay = true;
        else
            this.newProgram.lastDay = false;

         this._scope.$apply();

    }));
;

    $('#endDate').datetimepicker({
        format: 'MM/DD/YYYY'
    })
    .on('dp.change', angular.bind(this, function(e) {
        $('#endDate').data('DateTimePicker').minDate(  moment($('#startDate').val(), "MM/DD/YYYY") );
        this.newProgram.endDate = $('#endDate').val();
    }));
   /* $('#dueDate').datetimepicker({
        format: 'MM/DD/YYYY',
        minDate: moment().millisecond(0).second(0).minute(0).hour(0),
    })
    .on('dp.change', angular.bind(this, function(e) {
        this.newProgram.dueDate = $('#dueDate').val();
    }));*/
};

function ordinal_suffix_of(i) {
    var j = i % 10,
        k = i % 100;
    if (j == 1 && k != 11) {
        return i + "st";
    }
    if (j == 2 && k != 12) {
        return i + "nd";
    }
    if (j == 3 && k != 13) {
        return i + "rd";
    }
    return i + "th";
}