from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import VolunteerProfile

@login_required(login_url='/accounts/register/')
def volunteer_register(request):
    if hasattr(request.user, 'volunteerprofile'):
        messages.info(request, 'You have already registered as a volunteer!')
        return redirect('home')

    if request.method == 'POST':
        # Get help types (multiple checkboxes)
        help_types = request.POST.getlist('help_types')
        help_types_str = ', '.join(help_types)

        profile = VolunteerProfile(
            user=request.user,
            full_name=request.POST['full_name'],
            phone=request.POST['phone'],
            age=request.POST['age'],
            gender=request.POST['gender'],
            address=request.POST['address'],
            location=request.POST['location'],
            profession=request.POST['profession'],
            organization=request.POST.get('organization', ''),
            has_nss='has_nss' in request.POST,
            has_ncc='has_ncc' in request.POST,
            has_ngo='has_ngo' in request.POST,
            has_scouts='has_scouts' in request.POST,
            has_red_cross='has_red_cross' in request.POST,
            has_civil_defence='has_civil_defence' in request.POST,
            other_organisation=request.POST.get('other_organisation', ''),
            skills=request.POST['skills'],
            help_types=help_types_str,
            has_first_aid='has_first_aid' in request.POST,
            has_swimming='has_swimming' in request.POST,
            has_driving='has_driving' in request.POST,
            languages=request.POST.get('languages', 'Malayalam, English'),
            available_from=request.POST['available_from'],
            available_until=request.POST['available_until'],
            full_time='full_time' in request.POST,
            id_proof_number=request.POST['id_proof_number'],
        )
        profile.save()
        request.user.role = 'volunteer'
        request.user.save()
        messages.success(request, 'Volunteer registration submitted! Awaiting admin approval.')
        return redirect('volunteer_success')

    return render(request, 'volunteers/register.html')

def volunteer_success(request):
    return render(request, 'volunteers/success.html')

@login_required
def approve_volunteer(request, pk):
    if not (request.user.is_admin_user() or request.user.is_staff):
        messages.error(request, "Access denied.")
        return redirect('home')

    volunteer = get_object_or_404(VolunteerProfile, pk=pk)
    volunteer.is_approved = True
    volunteer.save()
    messages.success(request, f"Volunteer {volunteer.full_name} has been approved.")
    return redirect('admin_dashboard')

@login_required
def reject_volunteer(request, pk):
    if not (request.user.is_admin_user() or request.user.is_staff):
        messages.error(request, "Access denied.")
        return redirect('home')

    volunteer = get_object_or_404(VolunteerProfile, pk=pk)
    name = volunteer.full_name
    volunteer.delete()
    messages.success(request, f"Volunteer registration for {name} has been rejected.")
    return redirect('admin_dashboard')

@login_required
def assign_volunteer_camp(request):
    if request.user.role not in ('camp_head', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    if request.method == 'POST':
        from django.shortcuts import get_object_or_404
        volunteer_id = request.POST.get('volunteer_id')
        camp = getattr(request.user, 'camp', None)
        if volunteer_id and camp:
            volunteer = get_object_or_404(VolunteerProfile, id=volunteer_id)
            volunteer.assigned_camp = camp
            volunteer.save()
            messages.success(request, f"Volunteer {volunteer.full_name} assigned to your camp successfully!")
        else:
            messages.error(request, "Invalid volunteer selection or camp.")

    return redirect('camp_head_dashboard')

@login_required
def unassign_volunteer_camp(request, volunteer_id):
    if request.user.role not in ('camp_head', 'admin'):
        messages.error(request, "Access denied.")
        return redirect('home')

    from django.shortcuts import get_object_or_404
    volunteer = get_object_or_404(VolunteerProfile, id=volunteer_id)
    camp = getattr(request.user, 'camp', None)
    if request.user.role == 'admin' or (camp and volunteer.assigned_camp == camp):
        volunteer.assigned_camp = None
        volunteer.save()
        messages.success(request, f"Volunteer {volunteer.full_name} removed from your camp.")
    else:
        messages.error(request, "Access denied or mismatch in camp assignment.")

    return redirect('camp_head_dashboard')