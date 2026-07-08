from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Camp, Need
from .forms import NeedForm, CampForm
import json


def camp_list(request):
    district = request.GET.get('district', '')
    camps = Camp.objects.filter(is_active=True, status='approved')
    if district:
        camps = camps.filter(district=district)

    from .models import KERALA_DISTRICTS
    return render(request, 'camps/camp_list.html', {
        'camps': camps,
        'districts': KERALA_DISTRICTS,
        'selected_district': district,
    })


def camp_detail(request, pk):
    camp = get_object_or_404(Camp, pk=pk)
    if camp.status != 'approved':
        user = request.user
        can_view = False
        if user.is_authenticated:
            if user.role == 'admin' or user.is_staff:
                can_view = True
            elif user.role == 'panchayath_staff' and camp.panchayath == user:
                can_view = True
            elif user.role == 'camp_head' and user.camp == camp:
                can_view = True
            elif user.role == 'field_officer' and user.district == camp.district:
                can_view = True
            elif user.role == 'district_officer' and user.district == camp.district:
                can_view = True
        if not can_view:
            messages.error(request, "This camp is pending verification or approval.")
            return redirect('camp_list')

    user = request.user
    if user.is_authenticated and (
        user.role == 'admin' or user.is_staff
        or (user.role == 'camp_head' and user.camp == camp)
        or (user.role == 'panchayath_staff' and camp.panchayath == user)
    ):
        # Staff see all needs including pending/rejected
        needs = camp.needs.all().order_by('is_fulfilled', 'priority')
    else:
        # Public and other users: show verified + fulfilled needs
        # (exclude only rejected needs)
        needs = camp.needs.exclude(status='rejected').order_by('is_fulfilled', 'priority')

    return render(request, 'camps/camp_detail.html', {'camp': camp, 'needs': needs})


def camp_map(request):
    camps = Camp.objects.filter(is_active=True, status='approved')

    district_coords = {
        'Thiruvananthapuram': [8.5241,  76.9366],
        'Kollam':             [8.8932,  76.6141],
        'Pathanamthitta':     [9.2648,  76.7870],
        'Alappuzha':          [9.4981,  76.3388],
        'Kottayam':           [9.5916,  76.5222],
        'Idukki':             [9.9189,  77.1025],
        'Ernakulam':          [10.0159, 76.3419],
        'Thrissur':           [10.5276, 76.2144],
        'Palakkad':           [10.7867, 76.6548],
        'Malappuram':         [11.0510, 76.0711],
        'Kozhikode':          [11.2588, 75.7804],
        'Wayanad':            [11.6854, 76.1320],
        'Kannur':             [11.8745, 75.3704],
        'Kasaragod':          [12.4996, 74.9869],
    }

    camps_data = []
    for camp in camps:
        coords = district_coords.get(camp.district, [10.8505, 76.2711])
        import random
        lat = coords[0] + random.uniform(-0.05, 0.05)
        lng = coords[1] + random.uniform(-0.05, 0.05)
        urgent_needs = camp.needs.filter(priority='urgent', is_fulfilled=False).count()
        camps_data.append({
            'id':             camp.pk,
            'name':           camp.name,
            'location':       camp.location,
            'district':       camp.district,
            'people_count':   camp.people_count,
            'contact_person': camp.contact_person,
            'contact_phone':  camp.contact_phone,
            'urgent_needs':   urgent_needs,
            'lat':            lat,
            'lng':            lng,
        })

    return render(request, 'camps/camp_map.html', {
        'camps':      camps,
        'camps_json': json.dumps(camps_data),
    })


@login_required
def add_need(request):
    if request.user.role not in ('camp_head', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    is_admin = (request.user.role == 'admin')

    if request.method == 'POST':
        form = NeedForm(request.POST, show_camp=is_admin)
        if form.is_valid():
            need = form.save(commit=False)
            if not is_admin:
                if not request.user.camp:
                    messages.error(request, "You are not assigned to any camp.")
                    return redirect('camp_head_dashboard')
                need.camp = request.user.camp
                # Camp head adds need → goes to pending for field officer to verify
                need.status = 'pending'
                need.verified_by_panchayath    = False
                need.verified_by_field_officer = False
            else:
                need.camp = form.cleaned_data['camp']
                need.status = 'verified'
                need.verified_by_panchayath    = True
                need.verified_by_field_officer = True
            need.save()
            messages.success(request, f"Need '{need.item}' added. Pending Field Officer verification.")
            return redirect('admin_dashboard' if is_admin else 'camp_head_dashboard')
    else:
        form = NeedForm(show_camp=is_admin)

    return render(request, 'camps/need_form.html', {
        'form':  form,
        'title': 'Add Need',
    })


@login_required
def edit_need(request, pk):
    need = get_object_or_404(Need, pk=pk)

    if request.user.role == 'camp_head':
        if need.camp != request.user.camp:
            messages.error(request, "You do not have permission to edit this need.")
            return redirect('camp_head_dashboard')
    elif request.user.role == 'admin':
        pass
    else:
        messages.error(request, "Access denied.")
        return redirect('home')

    is_admin = (request.user.role == 'admin')

    if request.method == 'POST':
        form = NeedForm(request.POST, instance=need, show_camp=is_admin)
        if form.is_valid():
            need = form.save(commit=False)
            if is_admin:
                need.camp = form.cleaned_data['camp']
                need.status = 'verified'
                need.verified_by_panchayath    = True
                need.verified_by_field_officer = True
            else:
                # Camp head edits need → reset to pending for re-verification
                need.status = 'pending'
                need.verified_by_panchayath    = False
                need.verified_by_field_officer = False
            need.save()
            messages.success(request, f"Need '{need.item}' updated. Pending Field Officer verification.")
            return redirect('admin_dashboard' if is_admin else 'camp_head_dashboard')
    else:
        form = NeedForm(instance=need, show_camp=is_admin)
        if is_admin:
            form.fields['camp'].initial = need.camp

    return render(request, 'camps/need_form.html', {
        'form':  form,
        'title': 'Edit Need',
        'need':  need,
    })


@login_required
def delete_need(request, pk):
    need = get_object_or_404(Need, pk=pk)

    if request.user.role == 'camp_head':
        if need.camp != request.user.camp:
            messages.error(request, "You do not have permission to delete this need.")
            return redirect('camp_head_dashboard')
    elif request.user.role == 'admin':
        pass
    else:
        messages.error(request, "Access denied.")
        return redirect('home')

    if request.method == 'POST':
        item_name = need.item
        need.delete()
        messages.success(request, f"Need '{item_name}' deleted successfully.")

    return redirect('admin_dashboard' if request.user.role == 'admin' else 'camp_head_dashboard')


@login_required
def toggle_need_fulfillment(request, pk):
    need = get_object_or_404(Need, pk=pk)

    if request.user.role == 'camp_head':
        if need.camp != request.user.camp:
            messages.error(request, "You do not have permission to modify this need.")
            return redirect('camp_head_dashboard')
    elif request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('home')

    need.is_fulfilled = not need.is_fulfilled
    if need.is_fulfilled:
        need.quantity_received = need.quantity_needed
    need.save()

    messages.success(request, f"Need '{need.item}' status updated.")
    return redirect('admin_dashboard' if request.user.role == 'admin' else 'camp_head_dashboard')


@login_required
def create_camp(request):
    """
    Only Field Officers and Admins can create relief camps.
    Field Officer → status = 'pending' (needs District Officer + Admin approval).
                  → district is locked to their own district.
    Admin         → status = 'approved' (goes live immediately), any district allowed.
    """
    if request.user.role not in ('field_officer', 'admin'):
        messages.error(request, "Access denied. Only Field Officers can add relief camps.")
        return redirect('home')

    # Field officers can only add camps in their own district
    locked_district = request.user.district if request.user.role == 'field_officer' else None

    if request.method == 'POST':
        form = CampForm(request.POST, locked_district=locked_district)
        if form.is_valid():
            camp = form.save(commit=False)
            camp.created_by = request.user
            camp.status = 'approved' if request.user.role == 'admin' else 'pending'

            # Enforce district restriction for field officers (double-check even after form clean)
            if locked_district:
                camp.district = locked_district

            # Auto-assign panchayath officer for this camp's district
            from accounts.models import CustomUser as _CU
            panchayath_user = _CU.objects.filter(
                role='panchayath_staff',
                district=camp.district,
                is_approved=True,
            ).first()
            if panchayath_user:
                camp.panchayath = panchayath_user

            camp.save()
            messages.success(
                request,
                f"Relief Camp '{camp.name}' created successfully. "
                + ("" if request.user.role == 'admin'
                   else "Status: Pending verification by District Officer and Admin.")
            )
            return redirect('admin_dashboard' if request.user.role == 'admin' else 'field_officer_dashboard')
    else:
        form = CampForm(locked_district=locked_district)

    return render(request, 'camps/camp_form.html', {
        'form':            form,
        'title':           'Create Relief Camp',
        'locked_district': locked_district,
    })


@login_required(login_url='/field/login/')
def field_officer_dashboard(request):
    if request.user.role not in ('field_officer', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    district = request.user.district

    from accounts.models import CustomUser
    if request.user.role == 'field_officer':
        camps = Camp.objects.filter(
            district=district, is_active=True
        ).select_related('created_by').order_by('-created_at')

        my_camps = Camp.objects.filter(
            created_by=request.user, is_active=True
        ).order_by('-created_at')

        pending_camp_heads = CustomUser.objects.filter(
            role='camp_head',
            is_approved=False,
            approved_by_field_officer=False,
            camp__district=district,
        ).select_related('camp').order_by('-id')

        pending_needs = Need.objects.filter(
            status='pending',
            verified_by_field_officer=False,
            camp__district=district,
        ).select_related('camp').order_by('-id')

        verified_needs = Need.objects.filter(
            status='verified',
            camp__district=district,
        ).select_related('camp').order_by('-id')

        approved_camp_heads = CustomUser.objects.filter(
            role='camp_head',
            approved_by_field_officer=True,
            camp__district=district,
        ).select_related('camp').order_by('-id')

    else:  # admin
        camps = Camp.objects.filter(is_active=True).order_by('-created_at')

        my_camps = Camp.objects.filter(is_active=True).order_by('-created_at')

        pending_camp_heads = CustomUser.objects.filter(
            role='camp_head',
            is_approved=False,
            approved_by_field_officer=False,
        ).select_related('camp').order_by('-id')

        pending_needs = Need.objects.filter(
            status='pending',
            verified_by_field_officer=False,
        ).select_related('camp').order_by('-id')

        verified_needs = Need.objects.filter(
            status='verified',
        ).select_related('camp').order_by('-id')

        approved_camp_heads = CustomUser.objects.filter(
            role='camp_head',
            approved_by_field_officer=True,
        ).select_related('camp').order_by('-id')

    return render(request, 'camps/field_officer_dashboard.html', {
        'camps':                camps,
        'my_camps':             my_camps,
        'district':             district,
        'pending_camp_heads':   pending_camp_heads,
        'approved_camp_heads':  approved_camp_heads,
        'pending_needs':        pending_needs,
        'verified_needs':       verified_needs,
    })


@login_required
def verify_camp(request, pk):
    """
    District Officer verifies a camp (pending → verified).
    Can only verify camps in their own district.
    Admin can verify any camp.
    """
    if request.user.role not in ('district_officer', 'admin'):
        messages.error(request, "Access denied. Only District Officers can verify camps.")
        return redirect('home')

    camp = get_object_or_404(Camp, pk=pk)

    redirect_target = 'admin_dashboard' if request.user.role == 'admin' else 'district_officer_dashboard'

    if request.user.role != 'admin' and camp.district != request.user.district:
        messages.error(request, "Access denied. Camp is not in your district.")
        return redirect(redirect_target)

    if request.method == 'POST':
        camp.status = 'verified'
        camp.save()
        messages.success(request, f"Relief Camp '{camp.name}' verified. Pending Admin approval.")

    return redirect(redirect_target)


@login_required(login_url='/district/login/')
def district_officer_dashboard(request):
    if request.user.role not in ('district_officer', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    district = request.user.district

    from accounts.models import CustomUser

    # ── Pending camps awaiting district officer verification ──────────────────
    pending_camps = Camp.objects.filter(is_active=True, status='pending')
    if request.user.role != 'admin':
        pending_camps = pending_camps.filter(district=district)

    # ── Verified / approved camps ─────────────────────────────────────────────
    verified_camps = Camp.objects.filter(is_active=True, status__in=['verified', 'approved'])
    if request.user.role != 'admin':
        verified_camps = verified_camps.filter(district=district)

    # ── Camp heads pending district officer approval ───────────────────────────
    if request.user.role == 'district_officer':
        pending_camp_heads = CustomUser.objects.filter(
            role='camp_head',
            is_approved=False,
            approved_by_field_officer=True,
            approved_by_panchayath=False,
            camp__district=district,
        ).select_related('camp').order_by('-id')
    else:
        pending_camp_heads = CustomUser.objects.filter(
            role='camp_head',
            is_approved=False,
            approved_by_field_officer=True,
            approved_by_panchayath=False,
        ).select_related('camp').order_by('-id')

    # ── Camp heads already approved by district officer (activity log) ────────
    if request.user.role == 'district_officer':
        approved_camp_heads = CustomUser.objects.filter(
            role='camp_head',
            approved_by_panchayath=True,
            camp__district=district,
        ).select_related('camp').order_by('-id')
    else:
        approved_camp_heads = CustomUser.objects.filter(
            role='camp_head',
            approved_by_panchayath=True,
        ).select_related('camp').order_by('-id')

    # ── Verified needs in district (activities performed) ─────────────────────
    verified_needs = Need.objects.filter(status='verified')
    if request.user.role != 'admin':
        verified_needs = verified_needs.filter(camp__district=district)
    verified_needs = verified_needs.select_related('camp').order_by('-id')

    # ── Rejected needs in district ────────────────────────────────────────────
    rejected_needs = Need.objects.filter(status='rejected')
    if request.user.role != 'admin':
        rejected_needs = rejected_needs.filter(camp__district=district)
    rejected_needs = rejected_needs.select_related('camp').order_by('-id')

    # ── Summary counts for activity cards ─────────────────────────────────────
    total_camps_in_district    = Camp.objects.filter(is_active=True)
    total_needs_in_district    = Need.objects.all()
    if request.user.role != 'admin':
        total_camps_in_district  = total_camps_in_district.filter(district=district)
        total_needs_in_district  = total_needs_in_district.filter(camp__district=district)

    activity_stats = {
        'camps_verified':       verified_camps.filter(status='verified').count(),
        'camps_approved':       verified_camps.filter(status='approved').count(),
        'camp_heads_approved':  approved_camp_heads.count(),
        'needs_verified':       verified_needs.count(),
        'needs_rejected':       rejected_needs.count(),
        'needs_pending':        Need.objects.filter(
                                    status='pending',
                                    **({'camp__district': district} if request.user.role != 'admin' else {})
                                ).count(),
        'total_camps':          total_camps_in_district.count(),
        'total_needs':          total_needs_in_district.count(),
    }

    return render(request, 'camps/district_officer_dashboard.html', {
        'camps':               pending_camps,
        'verified_camps':      verified_camps,
        'district':            district,
        'pending_camp_heads':  pending_camp_heads,
        'approved_camp_heads': approved_camp_heads,
        'verified_needs':      verified_needs,
        'rejected_needs':      rejected_needs,
        'activity_stats':      activity_stats,
    })


@login_required
def approve_camp(request, pk):
    """
    Admin gives final approval (verified → approved). Camp becomes public.
    """
    if request.user.role != 'admin' and not request.user.is_staff:
        messages.error(request, "Access denied. Only Admin can give final approval to camps.")
        return redirect('home')

    camp = get_object_or_404(Camp, pk=pk)

    if request.method == 'POST':
        camp.status = 'approved'
        camp.save()
        messages.success(request, f"Relief Camp '{camp.name}' approved. It is now publicly visible.")

    return redirect('admin_dashboard')


@login_required
def verify_need(request, pk):
    if request.user.role not in ('field_officer', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    need = get_object_or_404(Need, pk=pk)

    if request.user.role == 'admin':
        need.verified_by_panchayath    = True
        need.verified_by_field_officer = True
        need.status = 'verified'
        need.save()
        messages.success(request, f"Need '{need.item}' verified by Admin.")
        return redirect('admin_dashboard')

    elif request.user.role == 'field_officer':
        if need.camp.district != request.user.district:
            messages.error(request, "Access denied. Camp is not in your district.")
            return redirect('field_officer_dashboard')
        need.verified_by_field_officer = True
        need.status = 'verified'
        need.save()
        messages.success(request, f"Need '{need.item}' verified. Now publicly visible.")
        return redirect('field_officer_dashboard')


@login_required
def reject_need(request, pk):
    if request.user.role not in ('field_officer', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    need = get_object_or_404(Need, pk=pk)

    if request.user.role == 'admin':
        need.status = 'rejected'
        need.save()
        messages.success(request, f"Need '{need.item}' rejected by Admin.")
        return redirect('admin_dashboard')

    elif request.user.role == 'field_officer':
        if need.camp.district != request.user.district:
            messages.error(request, "Access denied. Camp is not in your district.")
            return redirect('field_officer_dashboard')
        need.status = 'rejected'
        need.save()
        messages.success(request, f"Need '{need.item}' rejected by Field Officer.")
        return redirect('field_officer_dashboard')