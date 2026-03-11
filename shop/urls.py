from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index_view, name='home'),
    path('products/', views.products_catalog_view, name='products'),
    path('products/category/<slug:category_slug>/', views.products_catalog_view, name='products_by_category'),
    path('products/<int:product_id>/', views.product_detail_view, name='product_detail_legacy'),
    path('products/<int:product_id>/<slug:slug>/', views.product_detail_view, name='product_detail'),
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
    path('checkout/create/', views.create_checkout_session, name='create_checkout_session'),
    path('orders/create-from-product/', views.create_order_from_product, name='create_order_from_product'),
    path('orders/<int:order_id>/checkout/', views.create_checkout_session_for_order, name='create_checkout_session_for_order'),
    path('success/', views.checkout_success, name='success'),
    path('cancel/', views.checkout_cancel, name='cancel'),
    path('payments/success/', views.payment_success, name='payment_success'),
    path('payments/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payments/webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
]
