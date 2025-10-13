from django.urls import path, include
from rest_framework.routers import DefaultRouter

from Retrace.Product import views
from .api_views import RegisterView, CustomObtainAuthToken, ProfileUserViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileUserViewSet, basename='profileuser')
router.register(r'userprofiles', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomObtainAuthToken.as_view(), name='token'),
    path('Login/', views.login1, name='Login'),
    path('Register/', views.register1, name='Register'),
    path('Base/', views.home, name='Home'),
    path('Profile/', views.user_profile, name='UserProfile'),
    path('', include(router.urls)),

]
