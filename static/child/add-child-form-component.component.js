AddChildFormComponentController = function($http, $routeParams, $location) {
  console.log("add-child-form-component-controller running");
  var self = this;
  
  self.dateOfBirthPickerOpened = false;

  self.openDateOfBirthPicker = function() {
    console.log("Toggle Date picker: " + self.dateOfBirthPickerOpened);
    self.dateOfBirthPickerOpened = ! self.dateOfBirthPickerOpened;
  };

  self.$onInit = function() {
    self.dateOfBirthPickerOpened = false;
  };

  self.$onChanges = function(changes) {
    console.log("onChange in add-child-form-component-controller");
    if (changes.childInfo) {
      console.log("childInfo change: " + changes.childInfo.currentValue);
      self.childInfo = changes.childInfo.currentValue;
    }
  };
}