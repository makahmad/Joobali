from django.conf.urls import patterns, url

from users import views

urlpatterns = patterns('',
	url(r'^$', views.home),
	url(r'^edit', views.form),
)
