from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^listpayments', views.listPayments, name='listPayments'),
	url(r'^addpayment', views.add_payment, name='addPayment')
]
