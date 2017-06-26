from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.render_enrollment_home, name='enrollmentHome'),
    url(r'^listByChild', views.list_enrollment_by_child, name='listEnrollmentByChild'),
    url(r'^listStatuses', views.list_statuses, name='listAllStatuses'),
    url(r'^add', views.add_enrollment, name='addEnrollment'),
    url(r'^get', views.get_enrollment, name='getEnrollment'),
    url(r'^cancel', views.cancel_enrollment, name='cancelEnrollment'),
    url(r'^accept', views.accept_enrollment, name='acceptEnrollment'),
    url(r'^reactivate', views.reactivate_enrollment, name='reactivateEnrollment'),
    url(r'^resendInvitation', views.resent_enrollment_invitation, name='resendInvitation'),
    url(r'^setupautopay', views.setupAutopay, name='setupAutopay'),
]
