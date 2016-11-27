var TIME_FORMAT =  'hh:mm A';

AddProgramFormComponentController = function() {
    console.log('AddProgramFormComponentController running');

	this.initializeTimePickers();
};

AddProgramFormComponentController.prototype.initializeTimePickers = function() {
    $('#startDate').datetimepicker({
        format: 'MM/DD/YYYY',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        $('#endDate').data('DateTimePicker').minDate(e.date);
        this.newProgram.startDate = $('#startDate').val();
    }));

    $('#endDate').datetimepicker({
        format: 'MM/DD/YYYY',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        this.newProgram.endDate = $('#endDate').val();
    }));
    $('#dueDate').datetimepicker({
        format: 'MM/DD/YYYY',
        minDate: new Date(),
    })
    .on('dp.change', angular.bind(this, function(e) {
        this.newProgram.dueDate = $('#dueDate').val();
    }));
};
