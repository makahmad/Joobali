ProgramComponentController = function($uibModal, $log, $location) {
    console.log('ProgramComponentController running');
    this.location_ = $location;

     var $ctrl = this;

      $ctrl.animationsEnabled = true;

        $ctrl.openComponentModal = function () {
            $ctrl.program.css =0;

            var modalInstance = $uibModal.open({
              animation: $ctrl.animationsEnabled,
              component: 'editProgramComponent',
               resolve: {
                programId: function () {
                  return $ctrl.program.id;
                },
                confirmDeleteComponentModal: function () {
                  return $ctrl.confirmDeleteComponentModal;
                }

              }
            });

            modalInstance.result.then(function (selectedProgram) {
              $ctrl.program = selectedProgram;

                if($ctrl.program.indefinite)
                    $ctrl.program.endDate = "Indefinite";


            }, function () {
              $log.info('modal-component dismissed at: ' + new Date());
            });
          };


          $ctrl.confirmDeleteComponentModal = function () {
                var modalInstance = $uibModal.open({
                  animation: $ctrl.animationsEnabled,
                  component: 'confirmDeleteProgramComponent',
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

