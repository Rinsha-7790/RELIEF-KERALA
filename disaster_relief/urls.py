from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('transparency.urls')),
    path('accounts/', include('accounts.urls')),
    path('camps/', include('camps.urls')),
    path('donate/', include('donations.urls')),
    path('volunteer/', include('volunteers.urls')),
]