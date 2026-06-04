from .models import EmergencyAlert

def emergency_alerts(request):
    alerts = EmergencyAlert.objects.filter(is_active=True).order_by('-created_at')
    return {'emergency_alerts': alerts}