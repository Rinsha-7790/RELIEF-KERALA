from django.shortcuts import render, redirect
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