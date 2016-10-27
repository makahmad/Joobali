from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.render_enrollment_home, name='enrollmentHome'),
    url(r'^list', views.list_enrollment, name='listEnrollment'),
    url(r'^add', views.add_enrollment, name='addEnrollment'),
    url(r'^get', views.get_enrollment, name='getEnrollment')
]
