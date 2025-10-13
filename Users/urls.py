from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .import views
from .api_views import RegisterView, CustomObtainAuthToken, ProfileUserViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileUserViewSet, basename='profileuser')
router.register(r'userprofiles', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomObtainAuthToken.as_view(), name='token'),
    path('Login/', views.Login, name='Login'),
    path('Register/', views.Register, name='Register'),
    path('Base/', views.Home, name='Home'),
    path('Profile/', views.UserProfile, name='UserProfile'),
    path('', include(router.urls)),

]
