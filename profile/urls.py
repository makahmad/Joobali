from django.conf.urls import url

from profile import views

urlpatterns = [
	url(r'^getproviderlogo', views.getProviderLogo, name='getProviderLogo'),
	url(r'^getprofile', views.getProfile, name='getProfile'),
	url(r'^updateprofile', views.updateProfile, name='updateProfile'),
	url(r'^updatelogo', views.updateLogo, name='updateLogo'),
	url(r'^validateemail', views.validateEmail, name='validateEmail'),
	url(r'^dwollaverify', views.dwolla_verify, name='dwollaVerify'),
	url(r'^getdwollastatus', views.get_dwolla_status, name='getDwollaStatus'),
]
