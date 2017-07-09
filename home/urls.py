from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^dashboard', views.dashboard, name='dashboard'),
	url(r'^admin', views.admin, name='admin'),
]
