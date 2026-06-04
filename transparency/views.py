from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from donations.models import MoneyDonation, ItemDonation
from camps.models import Camp, Need
from volunteers.models import VolunteerProfile
from accounts.models import CustomUser
import json

def home(request):
    camps = Camp.objects.filter(is_active=True)
    total_money = MoneyDonation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_volunteers = VolunteerProfile.objects.filter(is_approved=True).count()
    total_camps = camps.count()
    urgent_needs = Need.objects.filter(priority='urgent', is_fulfilled=False)
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
    camps = Camp.objects.filter(is_active=True).prefetch_related('needs')
    context = {
        'money_donations': money_donations,
        'item_donations':  item_donations,
        'total_money':     total_money,
        'allocated':       allocated,
        'unallocated':     total_money - allocated,
        'camps':           camps,
    }
    return render(request, 'transparency/dashboard.html', context)

@login_required
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
    urgent_needs        = Need.objects.filter(priority='urgent', is_fulfilled=False).count()

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

    camps             = Camp.objects.filter(is_active=True).prefetch_related('needs')
    recent_money      = MoneyDonation.objects.order_by('-date')[:5]
    recent_items      = ItemDonation.objects.order_by('-created_at')[:5]
    recent_volunteers = VolunteerProfile.objects.order_by('-registered_at')[:5]

    panchayaths          = CustomUser.objects.filter(role='panchayath_staff').order_by('district')
    total_panchayaths    = panchayaths.count()
    total_item_donations = ItemDonation.objects.count()
    delivered_items      = ItemDonation.objects.filter(delivery_status='delivered').count()
    pending_items        = ItemDonation.objects.filter(delivery_status='registered').count()

    context = {
        'total_money':          total_money,
        'total_donors':         total_donors,
        'total_volunteers':     total_volunteers,
        'approved_volunteers':  approved_volunteers,
        'pending_volunteers':   pending_volunteers,
        'total_camps':          total_camps,
        'total_users':          total_users,
        'urgent_needs':         urgent_needs,
        'months_json':          json.dumps(months),
        'amounts_json':         json.dumps(amounts),
        'status_labels_json':   json.dumps(status_labels),
        'status_counts_json':   json.dumps(status_counts),
        'camps':                camps,
        'recent_money':         recent_money,
        'recent_items':         recent_items,
        'recent_volunteers':    recent_volunteers,
        'panchayaths':          panchayaths,
        'total_panchayaths':    total_panchayaths,
        'total_item_donations': total_item_donations,
        'delivered_items':      delivered_items,
        'pending_items':        pending_items,
    }
    return render(request, 'transparency/admin_dashboard.html', context)


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

    camps = Camp.objects.filter(is_active=True)

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
        'unallocated':        unallocated,
        'allocated_donations': allocated_donations,
        'camps':              camps,
    }
    return render(request, 'transparency/allocate_funds.html', context)