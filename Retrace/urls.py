"""
URL configuration for Retrace project.

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
from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
from django.conf import settings
from django.conf.urls.static import static
from AI.views import home, redirect_home
=======
from AI.views import home
>>>>>>> 8b1e1d938e70917f9e7bc0a124a56dd9f9496b7e

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('ai/', include('AI.urls')),
    path('Product/', include('Product.urls')),
<<<<<<< HEAD
    path('Users/', include('Users.urls')),
    path('users/', include('Users.urls')),  # Add lowercase version for user convenience
    path('Location/', include('Location.urls')),
    
    # Handle legacy .html URLs
    path('Home.html', redirect_home, name='home_legacy'),
    path('About.html', redirect_home, name='about_legacy'),
    path('Contact.html', redirect_home, name='contact_legacy'),
    path('Login.html', redirect_home, name='login_legacy'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
=======
    path('AI/', include('AI.urls')),
    path('Users/', include('Users.urls')),
    path('Location/', include('Location.urls')),
]
>>>>>>> 8b1e1d938e70917f9e7bc0a124a56dd9f9496b7e
