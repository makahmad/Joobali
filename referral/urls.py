from django.conf.urls import url

from referral import views

urlpatterns = [
	url(r'^$', views.referralForm),
	url(r'^list', views.list, name='list'),
]
