from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^getprofile', views.getProfile, name='getProfile'),
	url(r'^updateprofile', views.updateProfile, name='updateProfile'),
	url(r'^validateemail', views.validateEmail, name='validateEmail'),
]
