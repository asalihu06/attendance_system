from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('dashboard/', include('dashboard.urls')),
    path('', include('records.urls')),

    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='dashboard/login.html'),
        name='login'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page='/accounts/login/'),
        name='logout'
    ),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
