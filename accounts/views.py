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
    role = getattr(request.user, 'role', None)
    is_staff = getattr(request.user, 'is_staff', False)
    logout(request)
    messages.info(request, 'You have been logged out.')

    if is_staff or role in ('admin', 'field_officer', 'district_officer', 'panchayath_staff', 'camp_head'):
        return redirect('officials_portal')

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
            from .models import log_action
            log_action(request, 'register',
                       f"Admin registered Panchayath Officer: {panchayath_name} ({district})",
                       target_user=username)
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
            approved_by_panchayath    = is_approved,
            approved_by_field_officer = is_approved,
        )

        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff):
            messages.success(request, f'Camp Head {contact_person} registered successfully for {camp.name}.')
            return redirect('admin_dashboard')
        else:
            messages.success(request, 'Registration successful! Your account is pending approval from Field Officer and District Officer.')
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
    if request.user.role not in ('district_officer', 'admin'):
        messages.error(request, "Access denied. Only District Officers can approve Camp Coordinators.")
        return redirect('home')

    from .models import CustomUser
    camp_head = get_object_or_404(CustomUser, id=user_id, role='camp_head')

    if request.user.role != 'admin' and (not camp_head.camp or camp_head.camp.district != request.user.district):
        messages.error(request, "Access denied. Camp Coordinator's camp is not in your district.")
        return redirect('district_officer_dashboard')

    camp_head.approved_by_panchayath = True
    if camp_head.approved_by_field_officer:
        camp_head.is_approved = True
    camp_head.save()
    messages.success(request, f"Camp Coordinator {camp_head.contact_person or camp_head.username} approved by District Officer.")
    return redirect('district_officer_dashboard')

@login_required
def reject_camp_head_panchayath(request, user_id):
    if request.user.role not in ('district_officer', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    from .models import CustomUser
    camp_head = get_object_or_404(CustomUser, id=user_id, role='camp_head')
    if request.user.role != 'admin' and (not camp_head.camp or camp_head.camp.district != request.user.district):
        messages.error(request, "Access denied. Camp is not in your district.")
        return redirect('district_officer_dashboard')

    username = camp_head.username
    camp_head.delete()
    messages.success(request, f"Camp Coordinator registration for {username} has been rejected.")
    return redirect('district_officer_dashboard')

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
    messages.success(request, f"Camp Coordinator {camp_head.contact_person or camp_head.username} approved by Field Officer.")
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
    messages.success(request, f"Camp Coordinator registration for {username} has been rejected.")
    return redirect('field_officer_dashboard')


# ==============================================================================
# ROLE-SPECIFIC LOGINS AND DASHBOARDS
# ==============================================================================

def role_based_login(request, allowed_role, template_name, dashboard_name, portal_title, login_field='employee_id'):
    if request.user.is_authenticated:
        staff_roles = ('admin', 'panchayath_staff', 'camp_head', 'field_officer', 'district_officer')
        if request.user.is_staff or request.user.role in staff_roles:
            return redirect('profile')
        # Volunteer or donor visiting a staff login page — block them
        messages.error(
            request,
            'This login page is restricted to authorised Relief Kerala staff only.'
        )
        return redirect('home')

    if request.method == 'POST':
        identifier = request.POST.get(login_field, '').strip()
        password   = request.POST.get('password', '').strip()

        from .models import CustomUser
        from django.db.models import Q

        if not identifier:
            messages.error(request, 'Invalid credentials.')
            return redirect(request.path)

        if login_field == 'employee_id':
            user_obj = CustomUser.objects.filter(employee_id=identifier).first()
        else:
            # Donor / Volunteer portals accept either username or email.
            # Use filter().first() (never get()) since email isn't
            # guaranteed unique and a blank identifier used to match
            # every account with a blank value for that field.
            user_obj = CustomUser.objects.filter(
                Q(username=identifier) | Q(email=identifier)
            ).first()

        if user_obj is None:
            messages.error(request, 'Invalid credentials.')
        else:
            # Step 1: Check password first
            if not user_obj.check_password(password):
                messages.error(request, 'Invalid credentials.')
                return redirect(request.path)

            # Step 2: Check role match
            is_role_match = False
            if allowed_role == 'admin':
                if user_obj.role == 'admin' or user_obj.is_staff:
                    is_role_match = True
            else:
                if user_obj.role == allowed_role:
                    is_role_match = True

            if not is_role_match:
                messages.error(request, f"This login page is restricted to {portal_title} accounts.")
                return redirect(request.path)

            # Step 3: Check if pending approval
            if user_obj.role in ('panchayath_staff', 'camp_head', 'field_officer', 'district_officer') and not user_obj.is_approved:

                if user_obj.role == 'camp_head':
                    if not user_obj.approved_by_field_officer and not user_obj.approved_by_panchayath:
                        messages.warning(request, '⏳ Your account is pending approval from both Field Officer and District Officer. Please wait.')
                    elif not user_obj.approved_by_field_officer:
                        messages.warning(request, '⏳ Waiting for Field Officer approval. District Officer has already approved your account.')
                    elif not user_obj.approved_by_panchayath:
                        messages.warning(request, '⏳ Waiting for District Officer approval. Field Officer has already approved your account.')

                elif user_obj.role == 'field_officer':
                    messages.warning(request, '⏳ Your Field Officer account is pending Admin approval. Please wait.')

                elif user_obj.role == 'district_officer':
                    messages.warning(request, '⏳ Your District Officer account is pending Admin approval. Please wait.')

                elif user_obj.role == 'panchayath_staff':
                    messages.warning(request, '⏳ Your Panchayath Officer account is pending Admin approval. Please wait.')

                return redirect(request.path)

            # Step 4: All checks passed — log in
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                from .models import log_action
                log_action(request, 'login',
                           f"{portal_title} logged in via Employee ID portal.",
                           target_user=user.username)
                messages.success(request, f'Welcome back, {user.panchayath_name or user.first_name or user.username}!')
                return redirect(dashboard_name)
            else:
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
    return role_based_login(request, 'donor', 'accounts/donor_login.html', 'donor_dashboard', 'Donor', login_field='email')


def volunteer_login(request):
    return role_based_login(request, 'volunteer', 'accounts/volunteer_login.html', 'volunteer_dashboard', 'Volunteer', login_field='username')


def panchayath_login(request):
    return role_based_login(request, 'panchayath_staff', 'accounts/panchayath_login.html', 'panchayath_dashboard', 'Panchayath Officer')


def officials_portal(request):
    if request.user.is_authenticated:
        # Only staff roles should access the Officials Portal
        staff_roles = ('admin', 'panchayath_staff', 'camp_head', 'field_officer', 'district_officer')
        if request.user.is_staff or request.user.role in staff_roles:
            return redirect('profile')
        # Volunteers and donors are NOT allowed here — show an error
        messages.error(
            request,
            'This portal is restricted to authorised Relief Kerala staff only. '
            'Volunteers and donors do not have access to this area.'
        )
        return redirect('home')

    from django.conf import settings as django_settings
    portal_code = getattr(django_settings, 'OFFICIALS_PORTAL_CODE', None)

    if request.method == 'POST' and portal_code:
        entered_code = request.POST.get('access_code', '').strip()
        if entered_code != portal_code:
            messages.error(request, 'Invalid access code.')
            return render(request, 'accounts/officials_portal.html', {'requires_code': True})
        request.session['officials_portal_unlocked'] = True

    if portal_code and not request.session.get('officials_portal_unlocked'):
        return render(request, 'accounts/officials_portal.html', {'requires_code': True})

    return render(request, 'accounts/officials_portal.html', {'requires_code': False})


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
        camp_needs = volunteer_profile.assigned_camp.needs.filter(
            is_fulfilled=False,
            status='verified'
        ).order_by('priority')

    context = {
        'volunteer_profile': volunteer_profile,
        'camp_needs': camp_needs,
    }
    return render(request, 'accounts/volunteer_dashboard.html', context)