from django.conf.urls import url

from tasks import views

urlpatterns = [
	url(r'^invoicecalc', views.invoice_calculation, name='invoiceCalculation'),
]
