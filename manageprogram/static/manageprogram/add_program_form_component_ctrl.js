var TIME_FORMAT =  'hh:mm A';

AddProgramFormComponentController = function() {
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

    $('#endDate').datetimepicker({
        format: 'MM/DD/YYYY',
    })
    .on('dp.change', angular.bind(this, function(e) {
        console.log('fired2');
        this.newProgram.endDate = $('#endDate').val();
    }));
    $('#dueDate').datetimepicker({
        format: 'MM/DD/YYYY',
        minDate: moment().millisecond(0).second(0).minute(0).hour(0),
    })
    .on('dp.change', angular.bind(this, function(e) {
        this.newProgram.dueDate = $('#dueDate').val();
    }));
};
