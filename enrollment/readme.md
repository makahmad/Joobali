RESTFul Enrollment service
-

Restful API:
1. `/enrollment/listByChild/`, list all enrollments that a child has
2. `/enrollment/listStatuses`, list all possible enrollment statuses
3. `/enrollment/add`, a provider side client will call this to add new enrollment
4. `/enrollment/update`, a provider side client will call this to update an enrollment
5. `/enrollment/resendInvitation`, a provider side client will call this to resent invitation email to the parent
6. `/enrollment/get`, get one enrollment
7. `/enrollment/accept`, a parent side client will call this to accept an enrollment
8. `/enrollment/setupautopay`, a parent side client will call this to setup auto pay for an enrollment
