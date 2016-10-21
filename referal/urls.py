from django.conf.urls import url

from referal import views

urlpatterns = [
	url(r'^$', views.referalForm),
	url(r'^list', views.list, name='list'),
]
