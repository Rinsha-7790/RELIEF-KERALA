from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Camp, Need
import json

def camp_list(request):
    district = request.GET.get('district', '')
    camps = Camp.objects.filter(is_active=True)
    if district:
        camps = camps.filter(district=district)

    from .models import KERALA_DISTRICTS
    context = {
        'camps': camps,
        'districts': KERALA_DISTRICTS,
        'selected_district': district,
    }
    return render(request, 'camps/camp_list.html', context)

def camp_detail(request, pk):
    camp = get_object_or_404(Camp, pk=pk)
    needs = camp.needs.all().order_by('is_fulfilled', 'priority')
    return render(request, 'camps/camp_detail.html', {'camp': camp, 'needs': needs})

def camp_map(request):
    camps = Camp.objects.filter(is_active=True)

    # Kerala district coordinates
    district_coords = {
        'Thiruvananthapuram': [8.5241, 76.9366],
        'Kollam': [8.8932, 76.6141],
        'Pathanamthitta': [9.2648, 76.7870],
        'Alappuzha': [9.4981, 76.3388],
        'Kottayam': [9.5916, 76.5222],
        'Idukki': [9.9189, 77.1025],
        'Ernakulam': [10.0159, 76.3419],
        'Thrissur': [10.5276, 76.2144],
        'Palakkad': [10.7867, 76.6548],
        'Malappuram': [11.0510, 76.0711],
        'Kozhikode': [11.2588, 75.7804],
        'Wayanad': [11.6854, 76.1320],
        'Kannur': [11.8745, 75.3704],
        'Kasaragod': [12.4996, 74.9869],
    }

    camps_data = []
    for camp in camps:
        coords = district_coords.get(camp.district, [10.8505, 76.2711])
        # Add small offset so camps in same district don't overlap
        import random
        lat = coords[0] + random.uniform(-0.05, 0.05)
        lng = coords[1] + random.uniform(-0.05, 0.05)

        urgent_needs = camp.needs.filter(priority='urgent', is_fulfilled=False).count()
        camps_data.append({
            'id': camp.pk,
            'name': camp.name,
            'location': camp.location,
            'district': camp.district,
            'people_count': camp.people_count,
            'contact_person': camp.contact_person,
            'contact_phone': camp.contact_phone,
            'urgent_needs': urgent_needs,
            'lat': lat,
            'lng': lng,
        })

    context = {
        'camps': camps,
        'camps_json': json.dumps(camps_data),
    }
    return render(request, 'camps/camp_map.html', context)