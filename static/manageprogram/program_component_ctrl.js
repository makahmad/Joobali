ProgramComponentController = function($location) {
    console.log('ProgramComponentController running');
    this.location_ = $location;
}


ProgramComponentController.prototype.click = function() {
    this.location_.path('/program/' + this.program.id);
}