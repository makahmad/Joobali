from django.conf.urls import url

from users import views

urlpatterns = [
	url(r'^$', views.home),
	url(r'^edit', views.form),
]
