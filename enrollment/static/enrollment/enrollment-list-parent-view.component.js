EnrollmentListParentViewController = function EnrollmentListParentViewController($location) {
    this.location_ = $location;
    this.headers = [
        'Provider School Name',
        'Program Name',
        'Status',
        'Start Date',
        'Autopay?'
    ];
}

EnrollmentListParentViewController.prototype.viewDetail = function(enrollment) {
    console.log(enrollment);
    path = 'enrollmentview/' + enrollment.provider.id + '/' + enrollment.enrollment.id;
    console.log(path);
    this.location_.path(path);
}