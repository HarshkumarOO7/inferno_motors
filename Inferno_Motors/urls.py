# Inferno_Motors/urls.py (replace entire file with this)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home_1, name='home_1'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),

    # Feedback & misc
    path('send-feedback/', views.send_feedback, name='send_feedback'),
    path('google-login-callback/', views.google_login_callback, name='google_login_callback'),
    path('index/', views.index, name='index'),

    # Company & selection
    path('car_company/', views.car_copnany, name='car_copnany'),
    path('car_selection/', views.car_selection, name='car_selection'),
    path('get_car_models/<str:company_id>/', views.get_car_models, name='get_car_models'),
    path('get_car_parts/<str:model_id>/', views.get_car_parts, name='get_car_parts'),

    # Checkout & payment
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/confirm_order/', views.confirm_order, name='confirm_order'),
    path('payment-qr/', views.generate_qr_code, name='payment_qr'),

    # Selling & listings
    path('sell_car/', views.sell_car, name='sell_car'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('my_purchases/', views.my_purchases, name='my_purchases'),
    path('car-listings/', views.car_listings, name='car_listings'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('car/<int:car_id>/purchase/', views.purchase_request, name='purchase_request'),

    # API-like endpoints
    path('get_car_details/<int:car_id>/', views.get_car_details, name='get_car_details'),
    path('update_purchase_status/', views.update_purchase_status, name='update_purchase_status'),
    path('purchase_request/<int:request_id>/manage/', views.manage_purchase_request, name='manage_purchase_request'),
]
