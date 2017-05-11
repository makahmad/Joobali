var TIME_FORMAT =  'hh:mm A';

AddProgramFormComponentController = function($scope,$http) {
    console.log('AddProgramFormComponentController running');

	this.initializeTimePickers();

    var $ctrl = this;

//    $ctrl.weeklyBillDays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
//
//    $ctrl.monthlyBillDays = [];
//    for(var i=1;i<=28;i++)
//        $ctrl.monthlyBillDays.push(i);
//     $ctrl.monthlyBillDays.push("Last Day");

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
