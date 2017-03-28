from django.conf.urls import url

from verification import views

urlpatterns = [
    url(r'^provideremail', views.verify_provider_email)
]
