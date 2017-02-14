from django.conf.urls import url

from profile import views

urlpatterns = [
	url(r'^getprofile', views.getProfile, name='getProfile'),
	url(r'^updateprofile', views.updateProfile, name='updateProfile'),
	url(r'^validateemail', views.validateEmail, name='validateEmail'),
]
