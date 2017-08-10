from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^care', views.care, name='care'),
	url(r'^getprofile', views.getProfile, name='getProfile'),
	url(r'^updateprofile', views.updateProfile, name='updateProfile'),
	url(r'^validateemail', views.validateEmail, name='validateEmail'),
    url(r'^getautopaydata', views.get_autopay_data, name='getAutopayData'),
	url(r'^parentreferral', views.parentReferral, name='parentReferral'),
]
