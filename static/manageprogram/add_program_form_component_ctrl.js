var TIME_FORMAT =  'hh:mm A';

AddProgramFormComponentController = function($scope) {
    console.log('AddProgramFormComponentController running');

	this.initializeTimePickers();

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
<<<<<<< HEAD
        format: 'MM/DD/YYYY',
    })
    .on('dp.change', angular.bind(this, function(e) {
        console.log('fired2');
=======
        format: 'MM/DD/YYYY'
    })
    .on('dp.change', angular.bind(this, function(e) {
        $('#endDate').data('DateTimePicker').minDate(  moment($('#startDate').val(), "MM/DD/YYYY") );
>>>>>>> bec206e8da5f61f6017029d5afb46dce8811c663
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
