from django.conf.urls import url

from login import views

urlpatterns = [
	url(r'^signup', views.provider_signup),
	url(r'^parentsignup', views.parent_signup),
	url(r'^logout', views.logout),
	url(r'^$', views.login),
	url(r'^home', views.home),
]
