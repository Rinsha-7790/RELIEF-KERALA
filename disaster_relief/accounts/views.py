from django.shortcuts import render, redirect, get_object_or_404
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
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('donor_login')

@login_required
def profile(request):
    if request.user.is_staff or request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'panchayath_staff':
        return redirect('panchayath_dashboard')
    elif request.user.role == 'camp_head':
        return redirect('camp_head_dashboard')
    elif request.user.role == 'field_officer':
        return redirect('field_officer_dashboard')
    elif request.user.role == 'district_officer':
        return redirect('district_officer_dashboard')
    elif request.user.role == 'volunteer':
        return redirect('volunteer_dashboard')
    elif request.user.role == 'donor':
        return redirect('donor_dashboard')
    return redirect('home')

def panchayath_register(request):
    if request.method == 'POST':
        username        = request.POST.get('username', '').strip()
        password        = request.POST.get('password', '').strip()
        phone           = request.POST.get('phone', '').strip()
        panchayath_name = request.POST.get('panchayath_name', '').strip()
        district        = request.POST.get('district', '').strip()
        office_address  = request.POST.get('office_address', '').strip()
        contact_person  = request.POST.get('contact_person', '').strip()
        email           = request.POST.get('email', '').strip()
        employee_id     = request.POST.get('employee_id', '').strip()
        id_proof        = request.FILES.get('id_proof')

        from .models import CustomUser

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return redirect('panchayath_register')

        if email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email address already exists.')
            return redirect('panchayath_register')

        if not all([username, password, phone, panchayath_name, district, office_address, contact_person, email, employee_id, id_proof]):
            messages.error(request, 'Please fill in all fields and upload your ID proof.')
            return redirect('panchayath_register')

        is_approved = False
        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            is_approved = True

        # Create user
        user = CustomUser.objects.create_user(
            username        = username,
            email           = email,
            password        = password,
            phone           = phone,
            role            = 'panchayath_staff',
            panchayath_name = panchayath_name,
            district        = district,
            office_address  = office_address,
            contact_person  = contact_person,
            employee_id     = employee_id,
            id_proof        = id_proof,
            is_approved     = is_approved,
        )

        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            messages.success(request, f'Panchayath {panchayath_name} registered successfully.')
            return redirect('admin_dashboard')
        else:
            messages.success(request, 'Registration successful! Your account is pending admin approval. You will be able to log in once approved.')
            return redirect('panchayath_login')

    from .models import KERALA_DISTRICTS
    return render(request, 'accounts/panchayath_register.html', {
        'districts': KERALA_DISTRICTS,
    })

def camp_head_register(request):
    if request.method == 'POST':
        username       = request.POST.get('username', '').strip()
        password       = request.POST.get('password', '').strip()
        phone          = request.POST.get('phone', '').strip()
        contact_person = request.POST.get('contact_person', '').strip()
        camp_id        = request.POST.get('camp', '').strip()
        email          = request.POST.get('email', '').strip()
        employee_id    = request.POST.get('employee_id', '').strip()
        id_proof       = request.FILES.get('id_proof')

        from .models import CustomUser
        from camps.models import Camp

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('camp_head_register')

        if email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email address already exists.')
            return redirect('camp_head_register')

        if not all([username, password, phone, contact_person, camp_id, email, employee_id, id_proof]):
            messages.error(request, 'Please fill in all fields and upload your ID proof.')
            return redirect('camp_head_register')

        camp = Camp.objects.get(pk=camp_id)

        is_approved = False
        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            is_approved = True

        user = CustomUser.objects.create_user(
            username       = username,
            email          = email,
            password       = password,
            phone          = phone,
            role           = 'camp_head',
            contact_person = contact_person,
            camp           = camp,
            employee_id    = employee_id,
            id_proof       = id_proof,
            is_approved    = is_approved,
            approved_by_panchayath = is_approved,
            approved_by_field_officer = is_approved,
        )

        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            messages.success(request, f'Camp Head {contact_person} registered successfully for {camp.name}.')
            return redirect('admin_dashboard')
        else:
            messages.success(request, 'Registration successful! Your account is pending approval. You will be able to log in once approved by Panchayath and Field Officers.')
            return redirect('camp_login')

    from camps.models import Camp
    camps = Camp.objects.filter(is_active=True, status='approved')
    return render(request, 'accounts/camp_head_register.html', {
        'camps': camps,
    })

def staff_login(request):
    messages.error(request, "The staff login page is no longer public.")
    return redirect('home')

def field_officer_register(request):
    if request.method == 'POST':
        username       = request.POST.get('username', '').strip()
        password       = request.POST.get('password', '').strip()
        phone          = request.POST.get('phone', '').strip()
        contact_person = request.POST.get('contact_person', '').strip()
        district       = request.POST.get('district', '').strip()
        email          = request.POST.get('email', '').strip()
        employee_id    = request.POST.get('employee_id', '').strip()
        id_proof       = request.FILES.get('id_proof')

        from .models import CustomUser

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return redirect('field_officer_register')

        if email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email address already exists.')
            return redirect('field_officer_register')

        if not all([username, password, phone, contact_person, district, email, employee_id, id_proof]):
            messages.error(request, 'Please fill in all fields and upload your ID proof.')
            return redirect('field_officer_register')

        is_approved = False
        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            is_approved = True

        user = CustomUser.objects.create_user(
            username       = username,
            email          = email,
            password       = password,
            phone          = phone,
            role           = 'field_officer',
            contact_person = contact_person,
            district       = district,
            employee_id    = employee_id,
            id_proof       = id_proof,
            is_approved    = is_approved,
        )

        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            messages.success(request, f'Field Officer {contact_person} registered successfully.')
            return redirect('admin_dashboard')
        else:
            messages.success(request, 'Registration successful! Your account is pending admin approval. You will be able to log in once approved.')
            return redirect('field_login')

    from .models import KERALA_DISTRICTS
    return render(request, 'accounts/field_officer_register.html', {
        'districts': KERALA_DISTRICTS,
    })

def district_officer_register(request):
    if request.method == 'POST':
        username       = request.POST.get('username', '').strip()
        password       = request.POST.get('password', '').strip()
        phone          = request.POST.get('phone', '').strip()
        contact_person = request.POST.get('contact_person', '').strip()
        district       = request.POST.get('district', '').strip()
        email          = request.POST.get('email', '').strip()
        employee_id    = request.POST.get('employee_id', '').strip()
        id_proof       = request.FILES.get('id_proof')

        from .models import CustomUser

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return redirect('district_officer_register')

        if email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email address already exists.')
            return redirect('district_officer_register')

        if not all([username, password, phone, contact_person, district, email, employee_id, id_proof]):
            messages.error(request, 'Please fill in all fields and upload your ID proof.')
            return redirect('district_officer_register')

        is_approved = False
        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            is_approved = True

        user = CustomUser.objects.create_user(
            username       = username,
            email          = email,
            password       = password,
            phone          = phone,
            role           = 'district_officer',
            contact_person = contact_person,
            district       = district,
            employee_id    = employee_id,
            id_proof       = id_proof,
            is_approved    = is_approved,
        )

        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            messages.success(request, f'District Officer {contact_person} registered successfully.')
            return redirect('admin_dashboard')
        else:
            messages.success(request, 'Registration successful! Your account is pending admin approval. You will be able to log in once approved.')
            return redirect('district_login')

    from .models import KERALA_DISTRICTS
    return render(request, 'accounts/district_officer_register.html', {
        'districts': KERALA_DISTRICTS,
    })

@login_required
def approve_camp_head_panchayath(request, user_id):
    if request.user.role not in ('panchayath_staff', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    from .models import CustomUser
    camp_head = get_object_or_404(CustomUser, id=user_id, role='camp_head')
    if request.user.role != 'admin' and (not camp_head.camp or camp_head.camp.created_by != request.user):
        messages.error(request, "Access denied. You do not manage the camp for this Camp Head.")
        return redirect('panchayath_dashboard')

    camp_head.approved_by_panchayath = True
    if camp_head.approved_by_field_officer:
        camp_head.is_approved = True
    camp_head.save()
    messages.success(request, f"Camp Head {camp_head.contact_person or camp_head.username} approved by Panchayath.")
    return redirect('panchayath_dashboard')

@login_required
def reject_camp_head_panchayath(request, user_id):
    if request.user.role not in ('panchayath_staff', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    from .models import CustomUser
    camp_head = get_object_or_404(CustomUser, id=user_id, role='camp_head')
    if request.user.role != 'admin' and (not camp_head.camp or camp_head.camp.created_by != request.user):
        messages.error(request, "Access denied. You do not manage the camp for this Camp Head.")
        return redirect('panchayath_dashboard')

    username = camp_head.username
    camp_head.delete()
    messages.success(request, f"Camp Head registration for {username} has been rejected.")
    return redirect('panchayath_dashboard')

@login_required
def approve_camp_head_field_officer(request, user_id):
    if request.user.role not in ('field_officer', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    from .models import CustomUser
    camp_head = get_object_or_404(CustomUser, id=user_id, role='camp_head')
    if request.user.role != 'admin' and (not camp_head.camp or camp_head.camp.district != request.user.district):
        messages.error(request, "Access denied. Camp is not in your district.")
        return redirect('field_officer_dashboard')

    camp_head.approved_by_field_officer = True
    if camp_head.approved_by_panchayath:
        camp_head.is_approved = True
    camp_head.save()
    messages.success(request, f"Camp Head {camp_head.contact_person or camp_head.username} approved by Field Officer.")
    return redirect('field_officer_dashboard')

@login_required
def reject_camp_head_field_officer(request, user_id):
    if request.user.role not in ('field_officer', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    from .models import CustomUser
    camp_head = get_object_or_404(CustomUser, id=user_id, role='camp_head')
    if request.user.role != 'admin' and (not camp_head.camp or camp_head.camp.district != request.user.district):
        messages.error(request, "Access denied. Camp is not in your district.")
        return redirect('field_officer_dashboard')

    username = camp_head.username
    camp_head.delete()
    messages.success(request, f"Camp Head registration for {username} has been rejected.")
    return redirect('field_officer_dashboard')


# ==============================================================================
# ROLE-SPECIFIC LOGINS AND DASHBOARDS
# ==============================================================================

def role_based_login(request, allowed_role, template_name, dashboard_name, portal_title):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', '').strip()
        password    = request.POST.get('password', '').strip()
        try:
            from .models import CustomUser
            user = None

            # Look up by employee_id
            try:
                user_obj = CustomUser.objects.get(employee_id=employee_id)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass

            if user is not None:
                is_role_match = False
                if allowed_role == 'admin':
                    if user.role == 'admin' or user.is_staff:
                        is_role_match = True
                else:
                    if user.role == allowed_role:
                        is_role_match = True

                if not is_role_match:
                    messages.error(request, f"This login page is restricted to {portal_title} accounts.")
                    return redirect(request.path)

                if user.role in ('panchayath_staff', 'camp_head', 'field_officer', 'district_officer') and not getattr(user, 'is_approved', True):
                    messages.error(request, 'Your account is pending approval.')
                    return redirect(request.path)

                login(request, user)
                messages.success(request, f'Welcome back, {user.panchayath_name or user.first_name or user.username}!')
                return redirect(dashboard_name)
            else:
                messages.error(request, 'Invalid credentials.')
        except Exception as e:
            messages.error(request, 'Invalid credentials.')

    return render(request, template_name, {'portal_title': portal_title})


def district_login(request):
    return role_based_login(request, 'district_officer', 'accounts/district_login.html', 'district_officer_dashboard', 'District Officer')


def field_login(request):
    return role_based_login(request, 'field_officer', 'accounts/field_login.html', 'field_officer_dashboard', 'Field Officer')


def camp_login(request):
    return role_based_login(request, 'camp_head', 'accounts/camp_login.html', 'camp_head_dashboard', 'Camp Coordinator')


def admin_login(request):
    return role_based_login(request, 'admin', 'accounts/admin_login.html', 'admin_dashboard', 'Administrator')


def donor_login(request):
    return role_based_login(request, 'donor', 'accounts/donor_login.html', 'donor_dashboard', 'Donor')


def volunteer_login(request):
    return role_based_login(request, 'volunteer', 'accounts/volunteer_login.html', 'volunteer_dashboard', 'Volunteer')


def panchayath_login(request):
    return role_based_login(request, 'panchayath_staff', 'accounts/panchayath_login.html', 'panchayath_dashboard', 'Panchayath Officer')


def officials_portal(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'accounts/officials_portal.html')


@login_required(login_url='/donor/login/')
def donor_dashboard(request):
    if request.user.role != 'donor':
        messages.error(request, "Access denied.")
        return redirect('home')
    from donations.models import MoneyDonation, ItemDonation

    money_donations = MoneyDonation.objects.filter(
        donor=request.user
    ).order_by('-date')

    item_donations = ItemDonation.objects.filter(
        donor=request.user
    ).order_by('-created_at')

    total_donated = money_donations.aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    context = {
        'money_donations': money_donations,
        'item_donations': item_donations,
        'total_donated': total_donated,
        'donation_count': money_donations.count(),
        'item_count': item_donations.count(),
    }
    return render(request, 'accounts/donor_dashboard.html', context)


@login_required(login_url='/volunteer/login/')
def volunteer_dashboard(request):
    if request.user.role != 'volunteer':
        messages.error(request, "Access denied.")
        return redirect('home')
    from volunteers.models import VolunteerProfile

    volunteer_profile = None
    if hasattr(request.user, 'volunteerprofile'):
        volunteer_profile = request.user.volunteerprofile

    camp_needs = []
    if volunteer_profile and volunteer_profile.assigned_camp:
        camp_needs = volunteer_profile.assigned_camp.needs.filter(is_fulfilled=False, status='verified').order_by('priority')

    context = {
        'volunteer_profile': volunteer_profile,
        'camp_needs': camp_needs,
    }
    return render(request, 'accounts/volunteer_dashboard.html', context)
