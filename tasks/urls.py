from django.conf.urls import url

from tasks import views

urlpatterns = [
	url(r'^invoicecalc', views.invoice_calculation, name='invoiceCalculation'),
	url(r'^invoicenoti', views.invoice_notification, name='invoiceNotification'),
	url(r'^autopay', views.autopay, name='autopay'),
	url(r'^dwollawebhook', views.dwolla_webhook, name='dwollaWebhook'),
]
