from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index_view, name='home'),
    path('orders/create-from-product/', views.create_order_from_product, name='create_order_from_product'),
    path('orders/<int:order_id>/checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('payments/success/', views.payment_success, name='payment_success'),
    path('payments/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payments/webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
