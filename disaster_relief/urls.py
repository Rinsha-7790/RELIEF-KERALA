from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from accounts import views as accounts_views
from camps import views as camps_views
from donations import views as donations_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('transparency.urls')),
    path('accounts/', include('accounts.urls')),
    path('camps/', include('camps.urls')),
    path('donate/', include('donations.urls')),
    path('volunteer/', include('volunteers.urls')),

    # Role-specific login pages
    path('district/login/', accounts_views.district_login, name='district_login'),
    path('field/login/', accounts_views.field_login, name='field_login'),
    path('camp/login/', accounts_views.camp_login, name='camp_login'),
    path('admin-login/', accounts_views.admin_login, name='admin_login'),
    path('donor/login/', accounts_views.donor_login, name='donor_login'),
    path('volunteer/login/', accounts_views.volunteer_login, name='volunteer_login'),
    path('panchayath/login/', accounts_views.panchayath_login, name='panchayath_login'),

    # Role-specific dashboards
    path('donor/dashboard/', accounts_views.donor_dashboard, name='donor_dashboard'),
    path('volunteer/dashboard/', accounts_views.volunteer_dashboard, name='volunteer_dashboard'),
    path('district/dashboard/', camps_views.district_officer_dashboard, name='district_officer_dashboard'),
    path('field/dashboard/', camps_views.field_officer_dashboard, name='field_officer_dashboard'),
    path('camp/dashboard/', donations_views.camp_head_dashboard, name='camp_head_dashboard'),
    path('panchayath/dashboard/', donations_views.panchayath_dashboard, name='panchayath_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)