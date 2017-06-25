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
	url(r'^reset', views.reset),
	url(r'^termsofservice', views.terms_of_service),
	url(r'^privacypolicy', views.privacy_policy),
]
