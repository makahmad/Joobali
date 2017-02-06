ProgramComponentController = function($uibModal, $log, $location) {
    console.log('ProgramComponentController running');
    this.location_ = $location;

     var $ctrl = this;

      $ctrl.animationsEnabled = true;

        $ctrl.openComponentModal = function () {
            var modalInstance = $uibModal.open({
              animation: $ctrl.animationsEnabled,
              component: 'editProgramComponent',
               resolve: {
                programId: function () {
                  return $ctrl.program.id;
                }
              }
            });

            modalInstance.result.then(function (selectedProgram) {
              $ctrl.program = selectedProgram;
            }, function () {
              $log.info('modal-component dismissed at: ' + new Date());
            });
          };
}


ProgramComponentController.prototype.click = function() {

    this.location_.path('/program/' + this.program.id);
}

