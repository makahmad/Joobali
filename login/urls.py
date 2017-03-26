from django.conf.urls import url

from login import views

urlpatterns = [
	url(r'^signup', views.provider_signup),
	url(r'^forgot', views.forgot),
	url(r'^parentsignup', views.parent_signup),
	url(r'^logout', views.logout),
	url(r'^isinitsetupfinished', views.is_init_setup_finished),
	url(r'^setinitsetupfinished', views.set_init_setup_finished),
	url(r'^$', views.login),
	url(r'^home', views.home),
	url(r'^reset', views.reset),
]
