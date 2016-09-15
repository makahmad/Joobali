from django.conf.urls import url

from login import views

urlpatterns = [
	url(r'^$', views.form),
	url(r'^home', views.home),
]
