from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.render_enrollment_home, name='enrollmentHome'),
    url(r'^listByChild', views.list_enrollment_by_child, name='listEnrollmentByChild'),
    url(r'^add', views.add_enrollment, name='addEnrollment'),
    url(r'^addEnrollmentFromChildView', views.add_enrollment_from_child_view, name='addEnrollmentFromChildView'),
    url(r'^get', views.get_enrollment, name='getEnrollment'),
    url(r'^update', views.update_enrollment, name='updateEnrollment')
]
