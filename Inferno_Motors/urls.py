from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home_1, name='home_1'),
    path('login/',views.login,name="login"),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('send-feedback/', views.send_feedback, name='send_feedback'),  # Feedback form submission



    # Google OAuth Callback URL
    path('google-login-callback/', views.google_login_callback, name='google_login_callback'),  # Google OAuth callback

    # Additional Pages
    path('index/', views.index, name='index'),
    path('car_copnany/', views.car_copnany, name='car_copnany'),
    path('Car_Service_Booking/', views.Car_Service_Booking, name='Car_Service_Booking'),
    path('Car_Service_Booking/', views.Car_Service_Booking, name='Car_Service_Booking'),

    # Car Parts Functionality URLs
    path('car_selection/', views.car_selection, name='car_selection'),
    path('get_car_models/<str:company_id>/', views.get_car_models, name='get_car_models'),
    path('get_car_parts/<str:model_id>/', views.get_car_parts, name='get_car_parts'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-qr/', views.generate_qr_code, name='payment_qr'),
    path('checkout/confirm_order/', views.confirm_order, name='confirm_order'),
    path('payment-qr/', views.generate_qr_code, name='payment_qr'),


    # Car selling URLs
    path('sell_car/', views.sell_car, name='sell_car'),
    path('send-feedback/', views.send_feedback, name='send_feedback'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('my_purchases/', views.my_purchases, name='my_purchases'),
    path('update_purchase_status/', views.update_purchase_status, name='update_purchase_status'),
    path('car-listings/', views.car_listings, name='car_listings'),
    path('get_car_details/<int:car_id>/', views.get_car_details, name='get_car_details'),
    path('car/<int:car_id>/purchase/', views.purchase_request, name='purchase_request'),
    path('purchase_request/<int:request_id>/manage/', views.manage_purchase_request, name='manage_purchase_request'),
]