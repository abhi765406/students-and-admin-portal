"""
URL configuration for college_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('students/', include('students.urls')),
    path('students/password_reset/', auth_views.PasswordResetView.as_view(template_name='students/password_reset.html'), name='password_reset'),
    path('students/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='students/password_reset_done.html'), name='password_reset_done'),
    path('students/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='students/password_reset_confirm.html'), name='password_reset_confirm'),
    path('students/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='students/password_reset_complete.html'), name='password_reset_complete'),
    path('', RedirectView.as_view(url='/students/', permanent=False)),  # Add this line
]

# Media URL serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)