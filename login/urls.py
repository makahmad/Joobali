from django.conf.urls import url

from login import views

urlpatterns = [
	url(r'^signup', views.signup),
	url(r'^logout', views.logout),
	url(r'^$', views.login),
	url(r'^home', views.home),
]
