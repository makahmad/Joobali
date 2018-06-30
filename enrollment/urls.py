from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.render_enrollment_home, name='enrollmentHome'),
    url(r'^listByChild', views.list_enrollment_by_child, name='listEnrollmentByChild'),
    url(r'^listEnrollments', views.list_enrollments, name='listEnrollments'),
    url(r'^emailNonInvitedParents', views.email_non_invited_parents, name='emailNonInvitedParents'),
    url(r'^listStatuses', views.list_statuses, name='listAllStatuses'),
    url(r'^add', views.add_enrollment, name='addEnrollment'),
    url(r'^get', views.get_enrollment, name='getEnrollment'),
    url(r'^accept', views.accept_enrollment, name='acceptEnrollment'),
    url(r'^update', views.update_enrollment, name='updateEnrollment'),
    url(r'^resendInvitation', views.resent_enrollment_invitation, name='resendInvitation'),
    url(r'^setupautopay', views.setupAutopay, name='setupAutopay'),
    url(r'^cancelAutopay', views.cancelAutopay, name='cancelAutopay'),
]
