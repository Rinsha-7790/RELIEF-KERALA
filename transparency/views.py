from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from donations.models import MoneyDonation, ItemDonation
from camps.models import Camp, Need
from volunteers.models import VolunteerProfile
from accounts.models import CustomUser, AuditLog
import json

def home(request):
    camps = Camp.objects.filter(is_active=True, status='approved')
    total_money = MoneyDonation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_volunteers = VolunteerProfile.objects.filter(is_approved=True).count()
    total_camps = camps.count()
    urgent_needs = Need.objects.filter(priority='urgent', is_fulfilled=False, status='verified')
    context = {
        'camps': camps,
        'total_money': total_money,
        'total_volunteers': total_volunteers,
        'total_camps': total_camps,
        'urgent_needs': urgent_needs,
    }
    return render(request, 'transparency/home.html', context)

def dashboard(request):
    money_donations = MoneyDonation.objects.order_by('-date')[:20]
    item_donations  = ItemDonation.objects.order_by('-created_at')[:20]
    total_money = MoneyDonation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    allocated = MoneyDonation.objects.filter(
        status__in=['allocated', 'spent']
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    camps = Camp.objects.filter(is_active=True, status='approved').prefetch_related('needs')
    context = {
        'money_donations': money_donations,
        'item_donations':  item_donations,
        'total_money':     total_money,
        'allocated':       allocated,
        'unallocated':     total_money - allocated,
        'camps':           camps,
    }
    return render(request, 'transparency/dashboard.html', context)

@login_required(login_url='/admin-login/')
def admin_dashboard(request):
    if not request.user.is_admin_user() and not request.user.is_staff:
        return redirect('home')

    total_money         = MoneyDonation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_donors        = MoneyDonation.objects.values('donor_name').distinct().count()
    total_volunteers    = VolunteerProfile.objects.filter(is_approved=True).count()
    approved_volunteers = VolunteerProfile.objects.filter(is_approved=True).count()
    pending_volunteers  = VolunteerProfile.objects.filter(is_approved=False).count()
    total_camps         = Camp.objects.filter(is_active=True).count()
    total_users         = CustomUser.objects.count()
    urgent_needs        = Need.objects.filter(priority='urgent', is_fulfilled=False, status='verified').count()

    monthly = MoneyDonation.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')[:6]

    months  = [str(m['month'].strftime('%b %Y')) if m['month'] else '' for m in monthly]
    amounts = [float(m['total']) for m in monthly]

    status_data   = MoneyDonation.objects.values('status').annotate(count=Count('id'))
    status_labels = [s['status'] for s in status_data]
    status_counts = [s['count'] for s in status_data]

    camps = Camp.objects.filter(is_active=True).select_related(
        'panchayath', 'created_by'
    ).prefetch_related('needs', 'camp_heads').annotate(
        needs_count=Count('needs', distinct=True),
        unfulfilled_needs_count=Count(
            'needs', filter=Q(needs__is_fulfilled=False), distinct=True
        ),
        urgent_needs_count=Count(
            'needs',
            filter=Q(needs__priority='urgent', needs__is_fulfilled=False),
            distinct=True,
        ),
    ).order_by('district', 'name')
    recent_money      = MoneyDonation.objects.order_by('-date')[:5]
    recent_items      = ItemDonation.objects.order_by('-created_at')[:5]
    recent_volunteers = VolunteerProfile.objects.order_by('-registered_at')[:5]
    pending_volunteers_list = VolunteerProfile.objects.filter(
        is_approved=False
    ).select_related('user').order_by('-registered_at')

    approved_volunteers_list = VolunteerProfile.objects.filter(
        is_approved=True
    ).select_related('user').order_by('-registered_at')

    panchayaths             = CustomUser.objects.filter(role='panchayath_staff').order_by('district')
    total_panchayaths       = panchayaths.count()
    camp_heads              = CustomUser.objects.filter(role='camp_head').select_related('camp').order_by('district', 'camp__name')
    total_camp_heads        = camp_heads.count()
    field_officers          = CustomUser.objects.filter(role='field_officer').order_by('district', 'username')
    total_field_officers    = field_officers.count()
    district_officers       = CustomUser.objects.filter(role='district_officer').order_by('district', 'username')
    total_district_officers = district_officers.count()
    audit_logs              = AuditLog.objects.select_related('performed_by').order_by('-timestamp')[:50]
    total_item_donations    = ItemDonation.objects.count()
    delivered_items         = ItemDonation.objects.filter(delivery_status='delivered').count()
    pending_items           = ItemDonation.objects.filter(delivery_status='registered').count()

    verified_camps = Camp.objects.filter(
        is_active=True, status='verified'
    ).select_related('created_by').order_by('district', 'name')

    pending_staff = CustomUser.objects.filter(
        role__in=['panchayath_staff', 'camp_head', 'field_officer', 'district_officer'],
        is_approved=False
    ).select_related('camp').order_by('-id')

    context = {
        'total_money':             total_money,
        'total_donors':            total_donors,
        'total_volunteers':        total_volunteers,
        'approved_volunteers':     approved_volunteers,
        'pending_volunteers':      pending_volunteers,
        'total_camps':             total_camps,
        'total_users':             total_users,
        'urgent_needs':            urgent_needs,
        'months_json':             json.dumps(months),
        'amounts_json':            json.dumps(amounts),
        'status_labels_json':      json.dumps(status_labels),
        'status_counts_json':      json.dumps(status_counts),
        'camps':                   camps,
        'recent_money':            recent_money,
        'recent_items':            recent_items,
        'recent_volunteers':       recent_volunteers,
        'pending_volunteers_list':  pending_volunteers_list,
        'approved_volunteers_list': approved_volunteers_list,
        'panchayaths':             panchayaths,
        'total_panchayaths':       total_panchayaths,
        'camp_heads':              camp_heads,
        'total_camp_heads':        total_camp_heads,
        'field_officers':          field_officers,
        'total_field_officers':    total_field_officers,
        'district_officers':       district_officers,
        'total_district_officers': total_district_officers,
        'total_item_donations':    total_item_donations,
        'delivered_items':         delivered_items,
        'pending_items':           pending_items,
        'verified_camps':          verified_camps,
        'pending_staff':           pending_staff,
        'audit_logs':              audit_logs,
    }
    return render(request, 'transparency/admin_dashboard.html', context)


@login_required
def approve_staff(request, user_id):
    if not request.user.is_admin_user() and not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')

    staff_user = get_object_or_404(CustomUser, id=user_id)
    staff_user.is_approved = True
    staff_user.save()
    from accounts.models import log_action
    log_action(request, 'approve_staff',
               f"Approved {staff_user.get_role_display()} account: {staff_user.username}",
               target_user=staff_user.username)
    messages.success(request, f"Staff account for {staff_user.username} has been approved.")
    return redirect('admin_dashboard')


@login_required
def reject_staff(request, user_id):
    if not request.user.is_admin_user() and not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')

    staff_user = get_object_or_404(CustomUser, id=user_id)
    username = staff_user.username
    role_display = staff_user.get_role_display()
    staff_user.delete()
    from accounts.models import log_action
    log_action(request, 'reject_staff',
               f"Rejected and deleted {role_display} account: {username}",
               target_user=username)
    messages.success(request, f"Staff registration for {username} has been rejected (deleted).")
    return redirect('admin_dashboard')


@login_required
def allocate_funds(request):
    if not request.user.is_admin_user() and not request.user.is_staff:
        return redirect('home')

    unallocated = MoneyDonation.objects.filter(
        status='received'
    ).order_by('-date')

    allocated_donations = MoneyDonation.objects.filter(
        status__in=['allocated', 'spent']
    ).order_by('-date')

    camps = Camp.objects.filter(is_active=True, status='approved')

    if request.method == 'POST':
        donation_id = request.POST.get('donation_id')
        camp_id     = request.POST.get('camp_id')
        purpose     = request.POST.get('purpose', '').strip()

        try:
            donation = MoneyDonation.objects.get(id=donation_id)
            if camp_id:
                donation.camp   = Camp.objects.get(id=camp_id)
                donation.status = 'allocated'
            if purpose:
                donation.purpose = purpose
            donation.save()
            messages.success(request,
                f"₹{donation.amount} allocated to {donation.camp.name} successfully!")
        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect('allocate_funds')

    context = {
        'unallocated':         unallocated,
        'allocated_donations': allocated_donations,
        'camps':               camps,
    }
    return render(request, 'transparency/allocate_funds.html', context)