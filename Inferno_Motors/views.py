import requests
from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from django.views.decorators.csrf import csrf_exempt
import hashlib
import json
from .forms import *
import qrcode
import qrcode.image.pil
from django.http import HttpResponse
from io import BytesIO
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.serializers import serialize
import json
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
User = get_user_model()


# Create your views here.

def home_1(request):
    car = CarCompany.objects.all()
    part = CarPart.objects.all()
    return render(request, 'home.html',{'car':car ,'part':part})

def home(request):
    if 'name' in request.session:
        name = request.session['name']
        email = request.session['email']
        car= CarCompany.objects.all()
        part= CarPart.objects.all()
        return render(request, 'home.html', {'name': name, 'email': email , 'car':car , 'part':part})
    else:
        return render(request,"home.html")

def car_copnany(request):
    car=userdetails.objects.all()
    context = {
        'car':car,
    }
    return render(request,"home.html",context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')


        try:
            user = userdetails.objects.get(email=email)
            if user.password == password:
                # Set session variables
                request.session['name'] = user.name
                request.session['email'] = user.email
                request.session['user_id'] = user.id
                # In your login view
                request.session['user_email'] = user.email  # Instead of user.id
                messages.success(request, "Login successful!")
                return redirect('home')
            else:
                messages.error(request, "Invalid password.")
        except userdetails.DoesNotExist:
            messages.error(request, "Invalid email.")

        return redirect('login')

    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        contact = request.POST.get('contact')

        # Validation
        if userdetails.objects.filter(email=email).exists():
            messages.error(request, "Email already exists! Please use a different email.")
            return redirect('signup')
        if userdetails.objects.filter(name=name).exists():
            messages.error(request, "Username already exists! Please use a different email.")
            return redirect('signup')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('signup')

        # Create user
        user = userdetails(
            name=name,
            email=email,
            password=password,
            contact=contact,
        )
        # user.set_password(password)  # Hash the password
        user.save()  # Save the user object

        # Send welcome email
        subject = "Welcome to Inferno Motors!"
        message = f"Hello {user.name},\n\nWelcome to Inferno Motors! Thank you for registering with us.\n\nBest regards,\nInferno Motors Team"
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        messages.success(request, "Your account has been created successfully. Please log in.")
        return redirect('login')

    return render(request, 'login.html')

def signout(request):
    if 'name' in request.session:
        del request.session['name']
    if 'user_id' in request.session:
        del request.session['user_id']
    auth_logout(request)  # Logout the user
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

def send_feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f'New Feedback from {name}'
        email_message = f'Name: {name}\nEmail: {email}\nMessage: {message}'

        try:
            send_mail(
                subject,
                email_message,
                settings.EMAIL_HOST_USER,
                ['baraiyaharsh551@gmail.com'],  # Replace with your email address
                fail_silently=False,
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def index(request):
    return render(request, "index.html")

# Google OAuth Login Callback
def google_login_callback(request):
    if request.user.is_authenticated:
        # Fetch the SocialAccount object for the authenticated user
        social_account = SocialAccount.objects.get(user=request.user)
        extra_data = social_account.extra_data  # Contains Google OAuth data

        # Extract user details from Google OAuth
        name = extra_data.get('name', '')
        email = extra_data.get('email', '')

        # Save user details in your custom model
        if not userdetails.objects.filter(email=email).exists():
            userdetails.objects.create(
                name=name,
                email=email,
                password='',  # No password for Google OAuth users
                contact=''  # Optional
            )

        # Set session variables
        request.session['name'] = name
        request.session['email'] = email

        messages.success(request, "Login with Google successful!")
        return redirect('home')
    else:
        messages.error(request, "Google login failed. Please try again.")
        return redirect('login')

def compny_name(request):
    if request.POST:
        cpname = request.POST[""]
    context={
        'mode' : cpname,
    }
    return render(request,"home.html",context)

def Car_Service_Booking(request):
    return render(request,"Car_Service_Booking.html")

def car_selection(request):
    companies = CarCompany.objects.all()
    return render(request, 'car_selection.html', {'companies': companies})

def get_car_models(request, company_id):
    models = CarModel.objects.filter(company_id=company_id)
    model_data = [
        {
            'id': model.id,
            'name': model.name,
            'image': model.image.url if model.image else ''
        }
        for model in models
    ]
    return JsonResponse(model_data, safe=False)

def get_car_parts(request, model_id):
    parts = CarPart.objects.filter(car_model_id=model_id)
    part_data = [
        {
            'id': part.id,
            'name': part.name,
            'image': part.image.url if part.image else '',
            'price': str(part.price)
        }
        for part in parts
    ]
    return JsonResponse(part_data, safe=False)


@csrf_exempt
def checkout(request):
    # Get parameters from query string
    part_id = request.GET.get('part_id')
    quantity = request.GET.get('quantity', 1)  # Default to 1 if not provided

    if not part_id:
        return redirect('home')  # Redirect if no part_id is provided

    try:
        part = CarPart.objects.get(id=part_id)
        quantity = int(quantity)  # Convert to integer
    except (CarPart.DoesNotExist, ValueError):
        return redirect('home')

    if request.method == 'POST':
        # Get the user from the session
        user_email = request.session.get('user_email')
        try:
            user = userdetails.objects.get(email=user_email)
        except userdetails.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})

        # Validate all required fields
        required_fields = ['full_name', 'address_line1', 'city', 'state', 'pincode', 'phone']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]

        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            })

        # Validate PIN code (6 digits)
        pincode = request.POST.get('pincode')
        if not pincode.isdigit() or len(pincode) != 6:
            return JsonResponse({
                'success': False,
                'error': 'Invalid PIN code. Must be 6 digits.'
            })

        # Validate phone number (10 digits)
        phone = request.POST.get('phone')
        if not phone.isdigit() or len(phone) != 10:
            return JsonResponse({
                'success': False,
                'error': 'Invalid phone number. Must be 10 digits.'
            })

        # Check if payment is confirmed
        if not request.POST.get('payment_confirmed'):
            return JsonResponse({
                'success': False,
                'error': 'Please confirm that you have completed the payment.'
            })

        # Check if quantity is available
        if quantity > part.quantity:
            return JsonResponse({
                'success': False,
                'error': f'Only {part.quantity} units available. Please adjust your quantity.'
            })

        # Process the order if all validations pass
        address = f"{request.POST.get('full_name')}, {request.POST.get('address_line1')}, {request.POST.get('address_line2', '')}, {request.POST.get('city')}, {request.POST.get('state')} - {pincode}, Phone: {phone}"

        try:
            order = CarPartsPurchase(
                user=user,
                part=part,
                quantity=quantity,
                address=address,
                payment_status=True
            )
            order.save()

            # Reduce the part quantity in inventory
            part.quantity -= quantity
            part.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error processing order: {str(e)}'
            })

    return render(request, 'checkout.html', {
        'part': part,
        'quantity': quantity
    })
@never_cache
def generate_qr_code(request):
    # Get price from query parameters
    price = request.GET.get('price', '0')

    # Validate price is numeric
    try:
        float(price)
    except ValueError:
        return HttpResponse("Invalid price", status=400)

    # Create UPI payment link with dynamic amount
    upi_id = "your.upi.id@upi"  # Replace with your actual UPI ID
    payment_data = f"upi://pay?pa={upi_id}&pn=Inferno%20Motors&am={price}&tn=Car%20Parts%20Purchase&cu=INR"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payment_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save to buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")


@csrf_exempt
@transaction.atomic
def confirm_order(request):
    if request.method == 'POST':
        try:
            # Check session-based authentication
            if 'name' not in request.session:
                return JsonResponse({
                    'success': False,
                    'error': 'User not authenticated',
                    'redirect': '/login/'  # Add redirect URL for frontend
                })

            # Get user from session email (assuming you store email in session too)
            user_email = request.session.get('email')  # You should set this during login
            if not user_email:
                return JsonResponse({
                    'success': False,
                    'error': 'Session incomplete',
                    'redirect': '/login/'
                })

            try:
                user_detail = userdetails.objects.get(email=user_email)
            except userdetails.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'User account not found',
                    'redirect': '/login/'
                })

            # Process order data
            part_id = request.POST.get('part_id')
            quantity = int(request.POST.get('quantity'))
            part = CarPart.objects.get(id=part_id)

            if part.quantity < quantity:
                return JsonResponse({'success': False, 'error': 'Not enough stock available'})

            # Build address
            address_lines = [
                request.POST.get('full_name'),
                request.POST.get('address_line1'),
                request.POST.get('address_line2', ''),
                f"{request.POST.get('city')}, {request.POST.get('state')} - {request.POST.get('zip_code')}",
                f"Phone: {request.POST.get('phone')}"
            ]
            address = '\n'.join(filter(None, address_lines))

            # Create order
            order = CarPartsPurchase(
                user=user_detail,
                part=part,
                quantity=quantity,
                address=address,
                payment_status=True
            )
            order.save()

            # Update inventory
            part.quantity -= quantity
            part.save()

            # Send order confirmation email
            subject = f"Order Confirmation - #{order.id}"
            message = f"""
            Hello {user_detail.name},

            Thank you for your order with Inferno Motors! Here are your order details:

            Order ID: #{order.id}
            Part Ordered: {part.name}
            Quantity: {quantity}
            Total Amount: ₹{part.price * quantity}

            Shipping Address:
            {address}

            Your order will be processed and shipped soon. You'll receive another email with tracking information once it's shipped.

            If you have any questions, please contact our customer support.

            Best regards,
            Inferno Motors Team
            """
            from_email = settings.EMAIL_HOST_USER
            to_list = [user_detail.email]
            send_mail(subject, message.strip(), from_email, to_list, fail_silently=True)

            return JsonResponse({'success': True})

        except CarPart.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid part selected'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
# def sell_car(request):
#     return render(request,"sell_car.html")
#
# def sell_car_success(request):
#     return render(request,"sell_car_success.html")
#
# def my_listings(request):
#     pass

@csrf_exempt
@transaction.atomic
def sell_car(request):
    # Session-based authentication check
    if 'name' not in request.session:
        messages.warning(request, 'Please login to sell your car')
        return redirect('login')

    # Get user from session
    user_email = request.session.get('email')
    if not user_email:
        messages.warning(request, 'Session incomplete, please login again')
        return redirect('login')

    try:
        seller = userdetails.objects.get(email=user_email)
    except userdetails.DoesNotExist:
        messages.warning(request, 'User account not found')
        return redirect('login')

    if request.method == 'POST':
        # Validate required fields
        required_fields = ['make', 'model', 'year', 'price', 'mileage',
                           'fuel_type', 'transmission', 'color', 'engine_capacity',
                           'description', 'location', 'contact_number']

        errors = []
        data = request.POST.copy()

        # Basic validation
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")

        # Numeric field validation
        try:
            year = int(data.get('year', 0))
            if year < 1990 or year > 2023:
                errors.append("Year must be between 1990 and 2023")
        except ValueError:
            errors.append("Invalid year format")

        try:
            price = float(data.get('price', 0))
            if price < 100000:
                errors.append("Minimum price should be ₹1,00,000")
        except ValueError:
            errors.append("Invalid price format")

        # Image validation
        images = request.FILES.getlist('images')
        if len(images) < 3:
            errors.append("Please upload at least 3 images")

        if not errors:
            try:
                # Create car instance - using your custom user model
                car = Car(
                    seller=seller,  # This now uses your userdetails instance
                    make=data['make'],
                    model=data['model'],
                    year=year,
                    price=price,
                    mileage=int(data['mileage']),
                    fuel_type=data['fuel_type'],
                    transmission=data['transmission'],
                    color=data['color'],
                    engine_capacity=int(data['engine_capacity']),
                    description=data['description'],
                    location=data['location'],
                    contact_number=data['contact_number']
                )
                car.save()

                # Save images
                for i, image in enumerate(images):
                    file_name = default_storage.save(f'car_images/{image.name}', image)
                    CarImage.objects.create(
                        car=car,
                        image=file_name,
                        is_primary=(i == 0)
                    )

                # Send confirmation email
                subject = f"Your Car Listing is Live - {car.make} {car.model}"
                message = f"""
                Hello {seller.name},

                Thank you for listing your {car.year} {car.make} {car.model} with Inferno Motors!

                Listing Details:
                - Price: ₹{car.price:,.2f}
                - Mileage: {car.mileage} km
                - Location: {car.location}
                - Contact: {car.contact_number}

                Your listing is now live on our platform.

                Best regards,
                Inferno Motors Team
                """
                send_mail(
                    subject,
                    message.strip(),
                    settings.EMAIL_HOST_USER,
                    [seller.email],
                    fail_silently=True
                )

                messages.success(request, 'Your car has been listed successfully!')
                return redirect('car_listings')

            except Exception as e:
                errors.append(f"Error saving car: {str(e)}")
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in sell_car: {str(e)}")

        for error in errors:
            messages.error(request, error)

    return render(request, 'sell_car.html')
def car_listings(request):
    cars = Car.objects.filter(is_sold=False).order_by('-created_at')

    # Search functionality
    make = request.GET.get('make')
    model = request.GET.get('model')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if make:
        cars = cars.filter(make__icontains=make)
    if model:
        cars = cars.filter(model__icontains=model)
    if min_price:
        cars = cars.filter(price__gte=min_price)
    if max_price:
        cars = cars.filter(price__lte=max_price)

    # Pagination
    paginator = Paginator(cars, 9)  # Show 9 cars per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'car_listings.html', {'page_obj': page_obj})


def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'car_detail.html', {'car': car})


def purchase_request(request, car_id):
    if not request.session.get('name'):
        messages.warning(request, 'Please login to purchase a car')
        return redirect('login')

    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid():
            purchase_request = form.save(commit=False)
            purchase_request.car = car
            purchase_request.buyer = request.user
            purchase_request.save()

            messages.success(request, 'Your purchase request has been submitted!')
            return redirect('car_detail', car_id=car.id)
    else:
        initial = {'offer_price': car.price}  # Default to listing price
        form = PurchaseRequestForm(initial=initial)

    return render(request, 'purchase_request.html', {'form': form, 'car': car})


def my_listings(request):
    if not request.session.get('name'):
        messages.warning(request, 'Please login to view your listings')
        return redirect('login')
    userdetail = request.session.get('user_id')
    cars = Car.objects.filter(seller=userdetail).order_by('-created_at')
    return render(request, 'my_listings.html', {'cars': cars})


def my_purchases(request):
    if not request.session.get('name'):
        messages.warning(request, 'Please login to view your purchases')
        return redirect('login')

    # Get the logged-in user's email from session
    user_email = request.session.get('email')

    try:
        # Get the user instance
        userqwe = userdetails.objects.get(email=user_email)

        # Get all purchase requests where:
        # 1. The buyer is the current user
        # 2. The status is either 'accepted' or 'completed'
        purchases = PurchaseRequest.objects.filter(
            buyer=userqwe,
            status__in=['accepted', 'completed']
        ).select_related('car').order_by('-created_at')

    except userdetails.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('login')

    return render(request, 'my_purchases.html', {'purchases': purchases})


@csrf_exempt  # Only if you're not using CSRF middleware properly
def update_purchase_status(request):
    if not request.session.get('name'):
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)

    if request.method == 'POST':
        purchase_id = request.POST.get('purchase_id')
        new_status = request.POST.get('new_status')

        try:
            purchase = PurchaseRequest.objects.get(
                id=purchase_id,
                buyer__email=request.session.get('email'),
                status='accepted'  # Only allow updating from 'accepted' status
            )

            purchase.status = new_status
            purchase.save()

            return JsonResponse({'success': True})

        except PurchaseRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Purchase not found or not eligible for update'},
                                status=404)

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@csrf_exempt  # Temporary for testing, remove in production
def get_car_details(request, car_id):
    try:
        car = Car.objects.select_related('seller').get(id=car_id)
        images = [{'image': img.image.url} for img in car.images.all()]

        data = {
            'success': True,
            'car': {
                'id': car.id,
                'year': car.year,
                'make': car.make,
                'model': car.model,
                'price': str(car.price),  # Convert Decimal to string
                'mileage': car.mileage,
                'fuel_type': car.get_fuel_type_display(),
                'transmission': car.get_transmission_display(),
                'color': car.color,
                'engine_capacity': car.engine_capacity,
                'description': car.description,
                'contact_number': car.contact_number,
                'location': car.location,
            },
            'seller': {
                'name': car.seller.name,
                'email': car.seller.email,
            },
            'images': images
        }
        return JsonResponse(data)

    except Car.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Car not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def purchase_request(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # Check if user is logged in
    if 'email' not in request.session:
        messages.warning(request, 'Please login to make a purchase request')
        return redirect('login')

    try:
        buyer = userdetails.objects.get(email=request.session['email'])
    except userdetails.DoesNotExist:
        messages.warning(request, 'User account not found')
        return redirect('login')

    if request.method == 'POST':
        try:
            # Create purchase request
            purchase = PurchaseRequest(
                car=car,
                buyer_name=buyer.name,
                buyer_email=buyer.email,
                buyer_phone=request.POST.get('phone', buyer.contact),
                offer_price=request.POST.get('offer_price'),
                message=request.POST.get('message', ''),
                status='pending'
            )
            purchase.save()

            # Send email notifications
            send_purchase_emails(purchase, car, buyer)

            messages.success(request, 'Your purchase request has been submitted!')
            return redirect('car_details', car_id=car.id)

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    # Get primary image
    primary_image = car.images.filter(is_primary=True).first() or car.images.first()

    return render(request, 'purchase_request.html', {
        'car': car,
        'primary_image': primary_image,
        'user': buyer
    })


def send_purchase_emails(purchase, car, buyer):
    # Email to seller
    seller_subject = f"New Purchase Request for your {car.make} {car.model}"
    seller_message = f"""
    Hello {car.seller.name},

    You have received a purchase request for your {car.year} {car.make} {car.model}.

    Buyer: {buyer.name}
    Email: {buyer.email}
    Phone: {purchase.buyer_phone}
    Offer: ₹{purchase.offer_price}

    Message:
    {purchase.message}

    Please respond through your dashboard.

    Regards,
    Inferno Motors Team
    """
    send_mail(
        seller_subject,
        seller_message.strip(),
        settings.DEFAULT_FROM_EMAIL,
        [car.seller.email],
        fail_silently=False
    )

    # Email to buyer
    buyer_subject = f"Purchase Request Confirmation - {car.make} {car.model}"
    buyer_message = f"""
    Hello {buyer.name},

    Thank you for your interest in the {car.year} {car.make} {car.model}.

    Your offer of ₹{purchase.offer_price} has been submitted.
    The seller will contact you soon.

    Request ID: {purchase.id}
    Car: {car.year} {car.make} {car.model}
    Seller: {car.seller.name}

    Regards,
    Inferno Motors Team
    """
    send_mail(
        buyer_subject,
        buyer_message.strip(),
        settings.DEFAULT_FROM_EMAIL,
        [buyer.email],
        fail_silently=True
    )

@csrf_exempt
def manage_purchase_request(request, request_id):
    if 'email' not in request.session:
        return JsonResponse({'success': False, 'error': 'Authentication required'})

    try:
        user = userdetails.objects.get(email=request.session['email'])
        purchase_request = PurchaseRequest.objects.get(id=request_id, car__seller=user)

        if request.method == 'POST':
            action = request.POST.get('action')

            if action == 'accept':
                purchase_request.status = 'accepted'
                # Mark car as sold
                car = purchase_request.car
                car.is_sold = True
                car.save()

                # Send notification to buyer
                send_mail(
                    f"Your offer for {car.make} {car.model} has been accepted",
                    f"Congratulations! The seller has accepted your offer of ₹{purchase_request.offer_price}",
                    settings.EMAIL_HOST_USER,
                    [purchase_request.buyer_email],
                    fail_silently=True
                )

            elif action == 'reject':
                purchase_request.status = 'rejected'
                # Send notification to buyer
                send_mail(
                    f"Your offer for {purchase_request.car.make} {purchase_request.car.model}",
                    f"The seller has declined your offer of ₹{purchase_request.offer_price}",
                    settings.EMAIL_HOST_USER,
                    [purchase_request.buyer_email],
                    fail_silently=True
                )

            elif action == 'counter':
                counter_price = request.POST.get('counter_price')
                if counter_price:
                    purchase_request.status = 'countered'
                    purchase_request.counter_price = counter_price
                    # Send notification to buyer
                    send_mail(
                        f"Counter offer for {purchase_request.car.make} {purchase_request.car.model}",
                        f"The seller has countered your offer with ₹{counter_price}",
                        settings.EMAIL_HOST_USER,
                        [purchase_request.buyer_email],
                        fail_silently=True
                    )

            purchase_request.save()
            return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})