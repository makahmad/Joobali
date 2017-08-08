from django.conf.urls import url

from verification import views

urlpatterns = [
    url(r'^provideremail', views.verify_provider_email),
    url(r'^provider/email/resend',views.resend_provider_email_verification)
]
