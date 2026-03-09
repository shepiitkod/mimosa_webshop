from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index_view, name='home'),
    path('products/', views.index_view, name='products'),
    path('products/bento/', views.product_bento_view, name='product_bento'),
    path('products/rose/', views.product_rose_view, name='product_rose'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy/', views.confidential_view, name='privacy'),
    path('login/', views.login_view, name='login'),
    path('login/submit/', views.login_submit, name='login_submit'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('register/submit/', views.register_submit, name='register_submit'),
    path('profile/', views.profile_view, name='profile'),
    path('cart/', views.cart_detail, name='cart'),
    path('cart/detail/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('order/create/', views.order_create, name='order_create'),
    path('orders/create-from-product/', views.create_order_from_product, name='create_order_from_product'),
    path('orders/<int:order_id>/checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('payments/success/', views.payment_success, name='payment_success'),
    path('payments/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payments/webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
