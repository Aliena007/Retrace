from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Views import removed - using API-only routes
from .api_views import RegisterView, CustomObtainAuthToken, ProfileUserViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileUserViewSet, basename='profileuser')
router.register(r'userprofiles', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomObtainAuthToken.as_view(), name='token'),
    # Removed Login view
    # Removed Register view
    # Removed Base view
    path('Profile/', views.user_profile, name='UserProfile'),
    path('', include(router.urls)),

]
