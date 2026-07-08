from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import razorpay
from .models import MoneyDonation, ItemDonation
from camps.models import Camp
from accounts.models import log_action

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def money_donate(request):
    camps = Camp.objects.filter(is_active=True, status='approved')

    if request.method == 'POST':
        amount     = int(request.POST['amount'])
        donor_name = request.POST['donor_name']
        camp_id    = request.POST.get('camp')
        purpose    = request.POST.get('purpose', '')

        razorpay_order = client.order.create({
            'amount':          amount * 100,
            'currency':        'INR',
            'payment_capture': 1,
        })

        donation = MoneyDonation(
            donor_name=donor_name,
            amount=amount,
            purpose=purpose,
            status='allocated' if camp_id else 'received',
            transaction_id=razorpay_order['id'],
        )
        if camp_id:
            donation.camp = Camp.objects.get(pk=camp_id)
        if request.user.is_authenticated:
            donation.donor = request.user
        donation.save()

        # ✅ Audit log — money donation initiated
        camp_name = donation.camp.name if donation.camp else 'General Fund'
        log_action(
            request,
            action='donate_money',
            description=(
                f"Money donation of ₹{amount} initiated by '{donor_name}' "
                f"for '{camp_name}'. Razorpay Order: {razorpay_order['id']}."
            ),
            extra_data={
                'donor_name':        donor_name,
                'amount':            amount,
                'camp':              camp_name,
                'purpose':           purpose,
                'razorpay_order_id': razorpay_order['id'],
            }
        )

        return render(request, 'donations/payment.html', {
            'razorpay_key':      settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount':            amount * 100,
            'amount_display':    amount,
            'donor_name':        donor_name,
            'donation_id':       donation.id,
            'camps':             camps,
        })

    donor_name = ''
    if request.user.is_authenticated:
        full_name  = f"{request.user.first_name} {request.user.last_name}".strip()
        donor_name = full_name or request.user.username

    return render(request, 'donations/money_donate.html', {
        'camps':      camps,
        'donor_name': donor_name,
    })


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        data = request.POST
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id':   data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature':  data['razorpay_signature'],
            })
            donation = MoneyDonation.objects.get(
                transaction_id=data['razorpay_order_id']
            )
            donation.transaction_id = data['razorpay_payment_id']
            if not donation.status == 'allocated':
                donation.status = 'received'
            donation.save()

            # ✅ Audit log — payment confirmed
            camp_name = donation.camp.name if donation.camp else 'General Fund'
            log_action(
                request,
                action='donate_money',
                description=(
                    f"Payment of ₹{donation.amount} confirmed for '{donation.donor_name}'. "
                    f"Camp: '{camp_name}'. Payment ID: {data['razorpay_payment_id']}."
                ),
                extra_data={
                    'donor_name':         donation.donor_name,
                    'amount':             str(donation.amount),
                    'camp':               camp_name,
                    'razorpay_payment_id': data['razorpay_payment_id'],
                    'status':             donation.status,
                }
            )

            messages.success(request, 'Payment successful! Thank you for your donation.')
            return redirect('donation_success')
        except Exception:
            messages.error(request, 'Payment verification failed. Please contact support.')
            return redirect('money_donate')
    return redirect('home')


def item_donate(request):
    camps = Camp.objects.filter(is_active=True, status='approved')
    from accounts.models import CustomUser
    panchayaths = CustomUser.objects.filter(
        role='panchayath_staff'
    ).order_by('district', 'panchayath_name')

    if request.method == 'POST':
        donation = ItemDonation(
            donor_name     = request.POST['donor_name'],
            donor_phone    = request.POST['donor_phone'],
            item_name      = request.POST['item_name'],
            quantity       = request.POST['quantity'],
            unit           = request.POST.get('unit', ''),
            delivery_notes = request.POST.get('notes', ''),
        )

        camp_id = request.POST.get('camp')
        if camp_id and camp_id != 'general':
            donation.camp = Camp.objects.get(pk=camp_id)

        panchayath_id = request.POST.get('panchayath')
        if panchayath_id:
            donation.panchayath = CustomUser.objects.get(pk=panchayath_id)
        elif camp_id and camp_id != 'general':
            # Auto-assign panchayath officer for the camp's district
            try:
                camp_obj = Camp.objects.get(pk=camp_id)
                fallback = CustomUser.objects.filter(
                    role='panchayath_staff',
                    district=camp_obj.district,
                    is_approved=True,
                ).first()
                if fallback:
                    donation.panchayath = fallback
            except Camp.DoesNotExist:
                pass

        if request.user.is_authenticated:
            donation.donor = request.user
        donation.save()

        # ✅ Audit log — item donation registered
        camp_name       = donation.camp.name if donation.camp else 'General'
        panchayath_name = donation.panchayath.panchayath_name if donation.panchayath else 'Unassigned'
        log_action(
            request,
            action='donate_item',
            description=(
                f"Item donation registered: {donation.quantity} {donation.unit} of "
                f"'{donation.item_name}' by '{donation.donor_name}' "
                f"(Phone: {donation.donor_phone}). Camp: '{camp_name}'. "
                f"Panchayath: '{panchayath_name}'. Tracking ID: {donation.tracking_id}."
            ),
            extra_data={
                'tracking_id':    donation.tracking_id,
                'donor_name':     donation.donor_name,
                'donor_phone':    donation.donor_phone,
                'item_name':      donation.item_name,
                'quantity':       donation.quantity,
                'unit':           donation.unit,
                'camp':           camp_name,
                'panchayath':     panchayath_name,
            }
        )

        messages.success(request,
            f'Donation registered! Tracking ID: {donation.tracking_id}. '
            f'Drop your items at '
            f'{donation.panchayath.panchayath_name if donation.panchayath else "your nearest Panchayath"}.')
        return redirect('track_donation', tracking_id=donation.tracking_id)

    donor_name = donor_phone = ''
    if request.user.is_authenticated:
        donor_name  = request.user.get_full_name() or request.user.username
        donor_phone = getattr(request.user, 'phone', '') or ''

    return render(request, 'donations/item_donate.html', {
        'camps':       camps,
        'panchayaths': panchayaths,
        'donor_name':  donor_name,
        'donor_phone': donor_phone,
    })


def donation_success(request):
    return render(request, 'donations/success.html')


# ------------------------------------------------------------------
# PANCHAYATH DASHBOARD
# ------------------------------------------------------------------
@login_required(login_url='/panchayath/login/')
def panchayath_dashboard(request):
    if request.user.role not in ('panchayath_staff', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    if request.user.role == 'panchayath_staff':
        pending_items = ItemDonation.objects.filter(
            panchayath=request.user,
            delivery_status__in=['registered', 'at_panchayath'],
        ).order_by('-created_at')

        transit_items = ItemDonation.objects.filter(
            panchayath=request.user,
            delivery_status='in_transit',
        ).order_by('-dispatched_at')

        delivered_items = ItemDonation.objects.filter(
            panchayath=request.user,
            delivery_status='delivered',
        ).order_by('-received_at')[:10]

    else:
        pending_items = ItemDonation.objects.filter(
            delivery_status__in=['registered', 'at_panchayath']
        ).order_by('-created_at')

        transit_items = ItemDonation.objects.filter(
            delivery_status='in_transit'
        ).order_by('-dispatched_at')

        delivered_items = ItemDonation.objects.filter(
            delivery_status='delivered'
        ).order_by('-received_at')[:10]

    from camps.models import Need
    from accounts.models import CustomUser

    if request.user.role == 'panchayath_staff':
        pending_needs = Need.objects.filter(
            status='pending',
            camp__panchayath=request.user,
            verified_by_panchayath=False,
        ).order_by('-id')

        pending_camp_heads = CustomUser.objects.filter(
            role='camp_head',
            is_approved=False,
            approved_by_panchayath=False,
            camp__panchayath=request.user,
        ).select_related('camp').order_by('-id')

    else:
        pending_needs = Need.objects.filter(
            status='pending',
            verified_by_panchayath=False,
        ).order_by('-id')

        pending_camp_heads = CustomUser.objects.filter(
            role='camp_head',
            is_approved=False,
            approved_by_panchayath=False,
        ).select_related('camp').order_by('-id')

    return render(request, 'donations/panchayath_dashboard.html', {
        'pending_items':      pending_items,
        'transit_items':      transit_items,
        'delivered_items':    delivered_items,
        'panchayath_name':    request.user.panchayath_name,
        'district':           request.user.district,
        'pending_needs':      pending_needs,
        'pending_camp_heads': pending_camp_heads,
    })


@login_required
def panchayath_receive(request, donation_id):
    if request.user.role not in ('panchayath_staff', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    donation = get_object_or_404(ItemDonation, id=donation_id)

    if request.method == 'POST':
        donation.delivery_status    = 'at_panchayath'
        donation.panchayath_name    = request.POST.get('panchayath_name', '').strip()
        donation.panchayath_address = request.POST.get('panchayath_address', '').strip()
        donation.delivery_notes     = request.POST.get('delivery_notes', '').strip()
        donation.save()

        # ✅ Audit log — items received at panchayath
        log_action(
            request,
            action='update_delivery',
            description=(
                f"Items received at Panchayath for Tracking ID '{donation.tracking_id}'. "
                f"Donor: '{donation.donor_name}'. Item: {donation.quantity} {donation.unit} "
                f"of '{donation.item_name}'. Received by: {request.user.get_full_name() or request.user.username}."
            ),
            extra_data={
                'tracking_id':    donation.tracking_id,
                'delivery_status': 'at_panchayath',
                'donor_name':     donation.donor_name,
                'item_name':      donation.item_name,
                'received_by':    request.user.username,
            }
        )

        messages.success(request, f"Items from {donation.donor_name} marked as received.")
        return redirect('panchayath_dashboard')

    return render(request, 'donations/panchayath_receive.html', {'donation': donation})


@login_required
def panchayath_dispatch(request, donation_id):
    if request.user.role not in ('panchayath_staff', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    donation = get_object_or_404(ItemDonation, id=donation_id)

    # All approved camps needed for the camp-select dropdown (general donations)
    camps = Camp.objects.filter(is_active=True, status='approved').order_by('district', 'name')

    if request.method == 'POST':

        # ── Assign camp if this was a general (no-camp) donation ──
        if not donation.camp:
            camp_id = request.POST.get('camp_id', '').strip()
            if not camp_id:
                messages.error(request, "Please select a destination camp before dispatching.")
                return render(request, 'donations/panchayath_dispatch.html', {
                    'donation': donation,
                    'camps': camps,
                })
            donation.camp = get_object_or_404(Camp, pk=camp_id, is_active=True, status='approved')

        donation.delivery_status = 'in_transit'
        donation.dispatched_by   = request.POST.get('dispatched_by', '').strip()
        donation.dispatched_at   = timezone.now()
        notes = request.POST.get('delivery_notes', '').strip()
        if notes:
            donation.delivery_notes = (donation.delivery_notes + '\n' + notes).strip()
        donation.save()

        # ✅ Audit log — items dispatched to camp
        camp_name = donation.camp.name if donation.camp else 'Unknown Camp'
        log_action(
            request,
            action='update_delivery',
            description=(
                f"Items dispatched to camp for Tracking ID '{donation.tracking_id}'. "
                f"Donor: '{donation.donor_name}'. Item: {donation.quantity} {donation.unit} "
                f"of '{donation.item_name}'. Dispatched to: '{camp_name}'. "
                f"Dispatched by: '{donation.dispatched_by}'."
            ),
            extra_data={
                'tracking_id':    donation.tracking_id,
                'delivery_status': 'in_transit',
                'donor_name':     donation.donor_name,
                'item_name':      donation.item_name,
                'camp':           camp_name,
                'dispatched_by':  donation.dispatched_by,
            }
        )

        messages.success(request, f"Items dispatched to {camp_name} — Tracking ID {donation.tracking_id}.")
        return redirect('panchayath_dashboard')

    return render(request, 'donations/panchayath_dispatch.html', {
        'donation': donation,
        'camps': camps,
    })


# ------------------------------------------------------------------
# CAMP HEAD DASHBOARD
# ------------------------------------------------------------------
@login_required(login_url='/camp/login/')
def camp_head_dashboard(request):
    if request.user.role not in ('camp_head', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    if request.user.role == 'camp_head':
        transit_items = ItemDonation.objects.filter(
            camp=request.user.camp,
            delivery_status='in_transit',
        ).order_by('-dispatched_at')

        delivered_items = ItemDonation.objects.filter(
            camp=request.user.camp,
            delivery_status='delivered',
        ).order_by('-received_at')[:10]
    else:
        transit_items = ItemDonation.objects.filter(
            delivery_status='in_transit'
        ).order_by('-dispatched_at')

        delivered_items = ItemDonation.objects.filter(
            delivery_status='delivered'
        ).order_by('-received_at')[:10]

    needs = []
    if request.user.role == 'camp_head' and request.user.camp:
        needs = request.user.camp.needs.all().order_by('is_fulfilled', 'priority')

    camp = getattr(request.user, 'camp', None)
    camp_volunteers      = []
    available_volunteers = []
    if camp:
        from volunteers.models import VolunteerProfile
        camp_volunteers      = VolunteerProfile.objects.filter(assigned_camp=camp, is_approved=True)
        available_volunteers = VolunteerProfile.objects.filter(is_approved=True).exclude(assigned_camp=camp)

    return render(request, 'donations/camp_dashboard.html', {
        'transit_items':        transit_items,
        'delivered_items':      delivered_items,
        'camp':                 camp,
        'needs':                needs,
        'camp_volunteers':      camp_volunteers,
        'available_volunteers': available_volunteers,
    })


@login_required
def camp_confirm_delivery(request, donation_id):
    if request.user.role not in ('camp_head', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    donation = get_object_or_404(ItemDonation, id=donation_id)

    if request.method == 'POST':
        received_by = request.POST.get('received_by', '').strip()
        notes       = request.POST.get('notes', '').strip()

        donation.delivery_status = 'delivered'
        donation.received_by     = received_by
        donation.received_at     = timezone.now()
        if notes:
            donation.delivery_notes = (donation.delivery_notes + '\n' + notes).strip()
        donation.save()

        # ✅ Audit log — delivery confirmed at camp
        camp_name = donation.camp.name if donation.camp else 'Unknown Camp'
        log_action(
            request,
            action='update_delivery',
            description=(
                f"Delivery confirmed at camp for Tracking ID '{donation.tracking_id}'. "
                f"Donor: '{donation.donor_name}'. Item: {donation.quantity} {donation.unit} "
                f"of '{donation.item_name}'. Camp: '{camp_name}'. "
                f"Received by: '{received_by}'."
            ),
            extra_data={
                'tracking_id':    donation.tracking_id,
                'delivery_status': 'delivered',
                'donor_name':     donation.donor_name,
                'item_name':      donation.item_name,
                'camp':           camp_name,
                'received_by':    received_by,
            }
        )

        messages.success(request, f"Delivery confirmed for tracking ID {donation.tracking_id}!")
        return redirect('camp_head_dashboard')

    return render(request, 'donations/camp_confirm_delivery.html', {'donation': donation})


# ------------------------------------------------------------------
# PUBLIC TRACKING & TRANSPARENCY
# ------------------------------------------------------------------
def track_donation(request, tracking_id):
    donation = get_object_or_404(ItemDonation, tracking_id=tracking_id)

    STATUS_STEPS = [
        ('registered',    'Registered',        'fa-check-circle'),
        ('at_panchayath', 'At Panchayath',      'fa-building'),
        ('in_transit',    'In Transit to Camp', 'fa-truck'),
        ('delivered',     'Delivered',          'fa-heart'),
    ]

    status_keys   = [s[0] for s in STATUS_STEPS]
    current_index = status_keys.index(donation.delivery_status) \
        if donation.delivery_status in status_keys else 0

    return render(request, 'donations/track_donation.html', {
        'donation':      donation,
        'STATUS_STEPS':  STATUS_STEPS,
        'current_index': current_index,
    })


def item_transparency(request):
    all_items = ItemDonation.objects.all().select_related('camp', 'panchayath')

    if request.user.is_authenticated and request.user.role == 'camp_head':
        all_items = all_items.filter(camp=request.user.camp)

    total_count      = all_items.count()
    registered_count = all_items.filter(delivery_status='registered').count()
    transit_count    = all_items.filter(delivery_status='in_transit').count()
    delivered_count  = all_items.filter(delivery_status='delivered').count()

    status_filter = request.GET.get('status', '')
    items = all_items.order_by('-created_at')
    if status_filter:
        items = items.filter(delivery_status=status_filter)

    STATUS_CHOICES = [
        ('',              'All'),
        ('registered',    'Registered'),
        ('at_panchayath', 'At Panchayath'),
        ('in_transit',    'In Transit'),
        ('at_camp',       'At Camp'),
        ('delivered',     'Delivered'),
    ]

    return render(request, 'donations/item_transparency.html', {
        'items':            items,
        'STATUS_CHOICES':   STATUS_CHOICES,
        'status_filter':    status_filter,
        'total_count':      total_count,
        'registered_count': registered_count,
        'transit_count':    transit_count,
        'delivered_count':  delivered_count,
    })


def public_update(request, tracking_id):
    donation = get_object_or_404(ItemDonation, tracking_id=tracking_id)

    STATUS_FLOW = {
        'registered':    'at_panchayath',
        'at_panchayath': 'in_transit',
        'in_transit':    'at_camp',
        'at_camp':       'delivered',
        'delivered':     None,
    }
    STATUS_LABELS = {
        'registered':    'Registered',
        'at_panchayath': 'At Panchayath',
        'in_transit':    'In Transit',
        'at_camp':       'At Camp',
        'delivered':     'Delivered',
    }
    STATUS_INSTRUCTIONS = {
        'registered':    'Mark this as received at your Panchayath office',
        'at_panchayath': 'Mark this as dispatched to the relief camp',
        'in_transit':    'Mark this as received at the relief camp',
        'at_camp':       'Mark this as fully delivered to camp residents',
        'delivered':     None,
    }

    next_status = STATUS_FLOW.get(donation.delivery_status)

    if request.method == 'POST':
        updater_name = request.POST.get('updater_name', '').strip()
        notes        = request.POST.get('notes', '').strip()
        action       = request.POST.get('action', '').strip()

        if not updater_name:
            messages.error(request, 'Please enter your name.')
            return redirect('public_update', tracking_id=tracking_id)

        if action == 'at_panchayath':
            donation.delivery_status    = 'at_panchayath'
            donation.panchayath_name    = request.POST.get('panchayath_name', '').strip()
            donation.panchayath_address = request.POST.get('panchayath_address', '').strip()
            note_line = f"Received at Panchayath by {updater_name}"
        elif action == 'in_transit':
            donation.delivery_status = 'in_transit'
            donation.dispatched_by   = updater_name
            donation.dispatched_at   = timezone.now()
            note_line = f"Dispatched to camp by {updater_name}"
        elif action == 'at_camp':
            donation.delivery_status = 'at_camp'
            donation.received_by     = updater_name
            donation.received_at     = timezone.now()
            note_line = f"Received at camp by {updater_name}"
        elif action == 'delivered':
            donation.delivery_status = 'delivered'
            donation.received_by     = updater_name
            donation.received_at     = timezone.now()
            note_line = f"Delivered to residents by {updater_name}"
        else:
            messages.error(request, 'Invalid action.')
            return redirect('public_update', tracking_id=tracking_id)

        if notes:
            note_line += f" — {notes}"
        existing = donation.delivery_notes or ''
        donation.delivery_notes = (existing + '\n' + note_line).strip()
        donation.save()

        # ✅ Audit log — public status update
        log_action(
            request,
            action='update_delivery',
            description=(
                f"Public status update for Tracking ID '{tracking_id}': "
                f"status changed to '{STATUS_LABELS[donation.delivery_status]}' "
                f"by '{updater_name}'. Item: '{donation.item_name}'."
            ),
            extra_data={
                'tracking_id':    tracking_id,
                'delivery_status': donation.delivery_status,
                'updated_by':     updater_name,
                'item_name':      donation.item_name,
                'notes':          notes,
            }
        )

        messages.success(request,
            f"Status updated to '{STATUS_LABELS[donation.delivery_status]}' successfully!")
        return redirect('track_donation', tracking_id=tracking_id)

    return render(request, 'donations/public_update.html', {
        'donation':            donation,
        'next_status':         next_status,
        'STATUS_LABELS':       STATUS_LABELS,
        'STATUS_INSTRUCTIONS': STATUS_INSTRUCTIONS,
    })