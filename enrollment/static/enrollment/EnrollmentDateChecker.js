angular.module('joobali.base', []).service('EnrollmentDateChecker', function($log) {

  this.days = {
        'Sunday': 0,
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6
  };

  this.isEnrollmentDateDisabled = function(dateAndMode, program) {
    var result = false;
    if (dateAndMode.mode === 'day') {
        var today = moment(new Date());
        var date = moment([dateAndMode.date.getFullYear(), dateAndMode.date.getMonth(), dateAndMode.date.getDate()]);
        if (date.diff(today, 'days') < 5) {
            return true;
        }
        if (program != null && program.billingFrequency != null) {
            if (program.billingFrequency === 'Weekly') {
                result =  (dateAndMode.date.getDay() != this.days[program.weeklyBillDay]);
            } else if (program.billingFrequency === 'Monthly') {
                if (program.monthlyBillDay === 'Last Day') {
                    result = (dateAndMode.date.getDate() != date.daysInMonth());
                } else {
                    result = (dateAndMode.date.getDate() != program.monthlyBillDay);
                }
            }
        }

        if (program) {
            var programStartDate = moment(program.startDate);
            if (date < programStartDate) {
                return true;
            }
        }

    }
    return result;
  }

  this.isEnrollmentEndDateDisabled = function(dateAndMode, program, enrollmentStartDate) {
    $log.info("dateAndMode: " + angular.toJson(dateAndMode) + ", enrollmentStartDate: " + angular.toJson(enrollmentStartDate));
    if (dateAndMode.mode === 'day') {
        var date = moment([dateAndMode.date.getFullYear(), dateAndMode.date.getMonth(), dateAndMode.date.getDate()]);
        if (enrollmentStartDate) {
            $log.info(date <= enrollmentStartDate);
            if (date <= enrollmentStartDate) {
                return true;
            }
        }
        
        if (program) {
            if (program.endDate) {
                if (program.monthlyBillDay === 'Last Day') {
                    if (date.date() != date.daysInMonth()) {
                        return true;
                    }
                } else {
                    var programEndDate = moment(program.endDate);
                    if (date > programEndDate) {
                        return true;
                    }
                }
            }
        }
    }
    return this.isEnrollmentDateDisabled(dateAndMode, program);
  };
});