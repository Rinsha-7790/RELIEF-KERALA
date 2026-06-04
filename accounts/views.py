from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .forms import RegisterForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('email', '').strip()
        password          = request.POST.get('password', '').strip()
        try:
            from .models import CustomUser
            # Try email first, then username
            try:
                user_obj = CustomUser.objects.get(email=email_or_username)
            except CustomUser.DoesNotExist:
                user_obj = CustomUser.objects.get(username=email_or_username)

            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request,
                    f'Welcome back, {user.panchayath_name or user.first_name or user.username}!')
                if user.is_staff or user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'panchayath_staff':
                    return redirect('panchayath_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid credentials.')
        except:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'accounts/login.html', {})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def profile(request):
    from donations.models import MoneyDonation, ItemDonation
    from volunteers.models import VolunteerProfile

    money_donations = MoneyDonation.objects.filter(
        donor=request.user
    ).order_by('-date')

    item_donations = ItemDonation.objects.filter(
        donor=request.user
    ).order_by('-created_at')

    total_donated = money_donations.aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    volunteer_profile = None
    if hasattr(request.user, 'volunteerprofile'):
        volunteer_profile = request.user.volunteerprofile

    context = {
        'money_donations': money_donations,
        'item_donations': item_donations,
        'total_donated': total_donated,
        'volunteer_profile': volunteer_profile,
        'donation_count': money_donations.count(),
        'item_count': item_donations.count(),
    }
    return render(request, 'accounts/profile.html', context)

def panchayath_register(request):
    if request.method == 'POST':
        username        = request.POST.get('username', '').strip()
        password        = request.POST.get('password', '').strip()
        phone           = request.POST.get('phone', '').strip()
        panchayath_name = request.POST.get('panchayath_name', '').strip()
        district        = request.POST.get('district', '').strip()
        office_address  = request.POST.get('office_address', '').strip()
        contact_person  = request.POST.get('contact_person', '').strip()

        from .models import CustomUser

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return redirect('panchayath_register')

        if not all([username, password, phone, panchayath_name, district, office_address, contact_person]):
            messages.error(request, 'Please fill in all fields.')
            return redirect('panchayath_register')

        # Create user without email
        user = CustomUser.objects.create_user(
            username        = username,
            email           = '',
            password        = password,
            phone           = phone,
            role            = 'panchayath_staff',
            panchayath_name = panchayath_name,
            district        = district,
            office_address  = office_address,
            contact_person  = contact_person,
        )

        login(request, user)
        messages.success(request,
            f'Welcome! {panchayath_name} is now registered.')
        return redirect('panchayath_dashboard')

    from .models import KERALA_DISTRICTS
    return render(request, 'accounts/panchayath_register.html', {
        'districts': KERALA_DISTRICTS,
    })