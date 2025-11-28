import json
from io import BytesIO
import qrcode
import qrcode.image.pil
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from .forms import PurchaseRequestForm
# from django.db.models import Q
from django.contrib.auth import authenticate, login as auth_login

User = get_user_model()


def home_1(request):
    car = CarCompany.objects.all()
    part = CarPart.objects.all()
    return render(request, 'home.html', {'car': car, 'part': part})


def home(request):
    if request.session.get('name'):
        name = request.session['name']
        email = request.session['email']
        car = CarCompany.objects.all()
        part = CarPart.objects.all()
        return render(request, 'home.html', {'name': name, 'email': email, 'car': car, 'part': part})
    else:
        car = CarCompany.objects.all()
        part = CarPart.objects.all()
        return render(request, "home.html", {'car': car, 'part': part})


def car_copnany(request):
    car = userdetails.objects.all()
    context = {'car': car}
    return render(request, "home.html", context)


def login_view(request):
    if request.method == 'POST':
        # Read raw POST values (strip whitespace)
        email = (request.POST.get('email') or '').strip()
        password = (request.POST.get('password') or '').strip()

        # Debug logs (remove in production)
        print("LOGIN_POST:", {"email": email, "password_provided": bool(password)})

        user = authenticate(request, email=email, password=password)
        print("AUTH RESULT:", user)  # will print user object (or None)

        if user is not None:
            auth_login(request, user)
            request.session['name'] = user.name
            request.session['email'] = user.email
            request.session['user_id'] = user.id
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
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
            messages.error(request, "Username already exists! Please use a different username.")
            return redirect('signup')

        if not password or len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('signup')

        # Create user via manager helper
        try:
            user = userdetails.objects.create_user(email=email, name=name, password=password, contact=contact)
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect('signup')

        # Auto login
        user = authenticate(request, email=email, password=password)
        if user:
            auth_login(request, user)
            request.session['name'] = user.name
            request.session['email'] = user.email
            request.session['user_id'] = user.id

        # Send welcome email
        try:
            subject = "Welcome to Inferno Motors!"
            message = f"Hello {user.name},\n\nWelcome to Inferno Motors! Thank you for registering with us.\n\nBest regards,\nInferno Motors Team"
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
        except Exception:
            # Don't block signup if email sending fails
            pass

        messages.success(request, "Your account has been created successfully.")
        return redirect('home')

    return render(request, 'login.html')


def signout(request):
    for key in ('name', 'user_id', 'email', 'user_email'):
        if key in request.session:
            del request.session[key]
    auth_logout(request)
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
                ['baraiyaharsh551@gmail.com'],
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
        try:
            social_account = SocialAccount.objects.get(user=request.user)
            extra_data = social_account.extra_data
            name = extra_data.get('name', '')
            email = extra_data.get('email', '')

            if not userdetails.objects.filter(email=email).exists():
                userdetails.objects.create_user(name=name, email=email, password=None, contact='')

            request.session['name'] = name
            request.session['email'] = email

            messages.success(request, "Login with Google successful!")
            return redirect('home')
        except Exception:
            messages.error(request, "Google login failed. Please try again.")
            return redirect('login')
    else:
        messages.error(request, "Google login failed. Please try again.")
        return redirect('login')


def compny_name(request):
    if request.method == 'POST':
        cpname = request.POST.get("company_name", "")
    else:
        cpname = ""
    context = {'mode': cpname}
    return render(request, "home.html", context)


def Car_Service_Booking(request):
    return render(request, "Car_Service_Booking.html")


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
    part_id = request.GET.get('part_id')
    quantity = request.GET.get('quantity', 1)

    if not part_id:
        return redirect('home')

    try:
        part = CarPart.objects.get(id=part_id)
        quantity = int(quantity)
    except (CarPart.DoesNotExist, ValueError):
        return redirect('home')

    if request.method == 'POST':
        user_email = request.session.get('user_email') or request.session.get('email')
        try:
            user = userdetails.objects.get(email=user_email)
        except userdetails.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})

        required_fields = ['full_name', 'address_line1', 'city', 'state', 'pincode', 'phone']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]
        if missing_fields:
            return JsonResponse({'success': False, 'error': f'Missing required fields: {", ".join(missing_fields)}'})

        pincode = request.POST.get('pincode')
        if not pincode.isdigit() or len(pincode) != 6:
            return JsonResponse({'success': False, 'error': 'Invalid PIN code. Must be 6 digits.'})

        phone = request.POST.get('phone')
        if not phone.isdigit() or len(phone) != 10:
            return JsonResponse({'success': False, 'error': 'Invalid phone number. Must be 10 digits.'})

        if not request.POST.get('payment_confirmed'):
            return JsonResponse({'success': False, 'error': 'Please confirm that you have completed the payment.'})

        if quantity > part.quantity:
            return JsonResponse({'success': False, 'error': f'Only {part.quantity} units available. Please adjust your quantity.'})

        address = f"{request.POST.get('full_name')}, {request.POST.get('address_line1')}, {request.POST.get('address_line2', '')}, {request.POST.get('city')}, {request.POST.get('state')} - {pincode}, Phone: {phone}"

        try:
            order = CarPartsPurchase(user=user, part=part, quantity=quantity, address=address, payment_status=True)
            order.save()
            part.quantity -= quantity
            part.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error processing order: {str(e)}'})

    return render(request, 'checkout.html', {'part': part, 'quantity': quantity})


@never_cache
def generate_qr_code(request):
    price = request.GET.get('price', '0')
    try:
        float(price)
    except ValueError:
        return HttpResponse("Invalid price", status=400)

    upi_id = "your.upi.id@upi"
    payment_data = f"upi://pay?pa={upi_id}&pn=Inferno%20Motors&am={price}&tn=Car%20Parts%20Purchase&cu=INR"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payment_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")


@csrf_exempt
@transaction.atomic
def confirm_order(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'})

    if 'name' not in request.session:
        return JsonResponse({'success': False, 'error': 'User not authenticated', 'redirect': '/login/'})

    user_email = request.session.get('email')
    if not user_email:
        return JsonResponse({'success': False, 'error': 'Session incomplete', 'redirect': '/login/'})

    try:
        user_detail = userdetails.objects.get(email=user_email)
    except userdetails.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User account not found', 'redirect': '/login/'})

    try:
        part_id = request.POST.get('part_id')
        quantity = int(request.POST.get('quantity'))
        part = CarPart.objects.get(id=part_id)
    except (ValueError, CarPart.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Invalid part selected'})

    if part.quantity < quantity:
        return JsonResponse({'success': False, 'error': 'Not enough stock available'})

    address_lines = [
        request.POST.get('full_name'),
        request.POST.get('address_line1'),
        request.POST.get('address_line2', ''),
        f"{request.POST.get('city')}, {request.POST.get('state')} - {request.POST.get('zip_code')}",
        f"Phone: {request.POST.get('phone')}"
    ]
    address = '\n'.join(filter(None, address_lines))

    order = CarPartsPurchase(user=user_detail, part=part, quantity=quantity, address=address, payment_status=True)
    order.save()
    part.quantity -= quantity
    part.save()

    # send confirmation email (attempt, but non-blocking)
    try:
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

Your order will be processed and shipped soon.
"""
        from_email = settings.EMAIL_HOST_USER
        to_list = [user_detail.email]
        send_mail(subject, message.strip(), from_email, to_list, fail_silently=True)
    except Exception:
        pass

    return JsonResponse({'success': True})


@csrf_exempt
@transaction.atomic
def sell_car(request):
    if 'name' not in request.session:
        messages.warning(request, 'Please login to sell your car')
        return redirect('login')

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
        required_fields = ['make', 'model', 'year', 'price', 'mileage',
                           'fuel_type', 'transmission', 'color', 'engine_capacity',
                           'description', 'location', 'contact_number']
        errors = []
        data = request.POST.copy()

        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")

        # Numeric validation
        try:
            year = int(data.get('year', 0))
            if year < 1900 or year > 2100:
                errors.append("Year must be valid")
        except ValueError:
            errors.append("Invalid year format")

        try:
            price = float(data.get('price', 0))
            if price < 0:
                errors.append("Price must be non-negative")
        except ValueError:
            errors.append("Invalid price format")

        images = request.FILES.getlist('images')
        if len(images) < 3:
            errors.append("Please upload at least 3 images")

        if not errors:
            try:
                car = Car(
                    seller=seller,
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

                for i, image in enumerate(images):
                    file_name = default_storage.save(f'car_images/{image.name}', image)
                    CarImage.objects.create(car=car, image=file_name, is_primary=(i == 0))

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
                send_mail(subject, message.strip(), settings.EMAIL_HOST_USER, [seller.email], fail_silently=True)

                messages.success(request, 'Your car has been listed successfully!')
                return redirect('car_listings')

            except Exception as e:
                errors.append(f"Error saving car: {str(e)}")

        for error in errors:
            messages.error(request, error)

    return render(request, 'sell_car.html')


def car_listings(request):
    cars = Car.objects.filter(is_sold=False).order_by('-created_at')

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

    paginator = Paginator(cars, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'car_listings.html', {'page_obj': page_obj})


def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'car_detail.html', {'car': car})


def purchase_request(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if 'email' not in request.session:
        messages.warning(request, 'Please login to make a purchase request')
        return redirect('login')

    try:
        buyer = userdetails.objects.get(email=request.session['email'])
    except userdetails.DoesNotExist:
        messages.warning(request, 'User account not found')
        return redirect('login')

    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid():
            purchase_request_obj = form.save(commit=False)
            purchase_request_obj.car = car
            purchase_request_obj.buyer_name = buyer.name
            purchase_request_obj.buyer_email = buyer.email
            purchase_request_obj.buyer_phone = request.POST.get('phone', buyer.contact)
            purchase_request_obj.save()

            # send emails (non-blocking)
            send_purchase_emails(purchase_request_obj, car, buyer)
            messages.success(request, 'Your purchase request has been submitted!')
            return redirect('car_detail', car_id=car.id)
    else:
        initial = {'offer_price': car.price}
        form = PurchaseRequestForm(initial=initial)

    primary_image = car.images.filter(is_primary=True).first() or car.images.first()

    return render(request, 'purchase_request.html', {'form': form, 'car': car, 'primary_image': primary_image, 'user': buyer})


def send_purchase_emails(purchase, car, buyer):
    try:
        seller_subject = f"New Purchase Request for your {car.make} {car.model}"
        seller_message = f"""
Hello {car.seller.get_full_name()},

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
        send_mail(seller_subject, seller_message.strip(), settings.DEFAULT_FROM_EMAIL, [car.seller.email], fail_silently=False)
    except Exception:
        pass

    try:
        buyer_subject = f"Purchase Request Confirmation - {car.make} {car.model}"
        buyer_message = f"""
Hello {buyer.name},

Thank you for your interest in the {car.year} {car.make} {car.model}.

Your offer of ₹{purchase.offer_price} has been submitted.
The seller will contact you soon.

Request ID: {purchase.id}

Regards,
Inferno Motors Team
"""
        send_mail(buyer_subject, buyer_message.strip(), settings.DEFAULT_FROM_EMAIL, [buyer.email], fail_silently=True)
    except Exception:
        pass


@csrf_exempt
def manage_purchase_request(request, request_id):
    if 'email' not in request.session:
        return JsonResponse({'success': False, 'error': 'Authentication required'})

    try:
        user = userdetails.objects.get(email=request.session['email'])
        purchase_request_obj = PurchaseRequest.objects.get(id=request_id, car__seller=user)

        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'accept':
                purchase_request_obj.status = 'accepted'
                purchase_request_obj.car.is_sold = True
                purchase_request_obj.car.save()
                send_mail(
                    f"Your offer for {purchase_request_obj.car.make} {purchase_request_obj.car.model} has been accepted",
                    f"Congratulations! The seller has accepted your offer of ₹{purchase_request_obj.offer_price}",
                    settings.EMAIL_HOST_USER,
                    [purchase_request_obj.buyer_email],
                    fail_silently=True
                )

            elif action == 'reject':
                purchase_request_obj.status = 'rejected'
                send_mail(
                    f"Your offer for {purchase_request_obj.car.make} {purchase_request_obj.car.model}",
                    f"The seller has declined your offer of ₹{purchase_request_obj.offer_price}",
                    settings.EMAIL_HOST_USER,
                    [purchase_request_obj.buyer_email],
                    fail_silently=True
                )

            elif action == 'counter':
                counter_price = request.POST.get('counter_price')
                if counter_price:
                    purchase_request_obj.status = 'countered'
                    purchase_request_obj.counter_price = counter_price
                    send_mail(
                        f"Counter offer for {purchase_request_obj.car.make} {purchase_request_obj.car.model}",
                        f"The seller has countered your offer with ₹{counter_price}",
                        settings.EMAIL_HOST_USER,
                        [purchase_request_obj.buyer_email],
                        fail_silently=True
                    )

            purchase_request_obj.save()
            return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


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
                'price': str(car.price),
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
                'name': getattr(car.seller, 'name', ''),
                'email': getattr(car.seller, 'email', ''),
            },
            'images': images
        }
        return JsonResponse(data)
    except Car.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Car not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def my_purchases(request):
    """
    Show purchases for the currently logged-in user.
    This version expects the PurchaseRequest model to store buyer_email (string).
    It returns purchase requests where the buyer_email matches the session user email
    and the status is either 'accepted' or 'completed'.
    """
    if not request.session.get('email'):
        messages.warning(request, 'Please login to view your purchases')
        return redirect('login')

    user_email = request.session.get('email')

    try:
        # Ensure there is a user record (optional, but helpful for email-based users)
        buyer = userdetails.objects.get(email=user_email)
    except userdetails.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('login')

    # Filter purchase requests for this buyer by email
    purchases = PurchaseRequest.objects.filter(
        buyer_email__iexact=user_email,
        status__in=['accepted', 'completed']
    ).select_related('car').order_by('-created_at')

    return render(request, 'my_purchases.html', {'purchases': purchases})

@csrf_exempt  # keep as in your original; remove in production
def update_purchase_status(request):
    """
    Allows a buyer (from session) to update the status of a purchase they made.
    This implementation expects PurchaseRequest to have a buyer_email field
    and status field. It only allows updating if the purchase currently has
    status 'accepted' (as in your earlier code).
    """
    if not request.session.get('email'):
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)

    if request.method == 'POST':
        purchase_id = request.POST.get('purchase_id')
        new_status = request.POST.get('new_status')

        if not purchase_id or not new_status:
            return JsonResponse({'success': False, 'message': 'Missing parameters'}, status=400)

        try:
            purchase = PurchaseRequest.objects.get(
                id=purchase_id,
                buyer_email__iexact=request.session.get('email'),
                status='accepted'  # only allow updates from 'accepted' status
            )

            # Validate allowed transitions (you can extend this logic)
            allowed = {'accepted': ['completed'], 'pending': ['accepted', 'rejected']}
            current = purchase.status
            if current not in allowed or new_status not in allowed.get(current, []):
                # allow changing from accepted -> completed explicitly
                if not (current == 'accepted' and new_status == 'completed'):
                    # If not allowed, still allow changing to same status for idempotency
                    if new_status != current:
                        return JsonResponse({'success': False, 'message': 'Status transition not allowed'}, status=400)

            purchase.status = new_status
            purchase.save()
            return JsonResponse({'success': True})
        except PurchaseRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Purchase not found or not eligible for update'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def my_listings(request):
    if not request.session.get('name'):
        messages.warning(request, 'Please login to view your listings')
        return redirect('login')
    user_id = request.session.get('user_id')
    cars = Car.objects.filter(seller_id=user_id).order_by('-created_at')
    return render(request, 'my_listings.html', {'cars': cars})


# compatibility aliases (if you renamed views earlier)
login = login_view
# other aliases you might need:
# purchase_request_old = purchase_request
