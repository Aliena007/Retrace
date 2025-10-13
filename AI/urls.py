from django.urls import path, include
from rest_framework.routers import DefaultRouter

from Retrace.AI import views
from .api_views import LostProductViewSet, FoundProductViewSet, MatchResultViewSet, NotificationViewSet, RouteMapViewSet

router = DefaultRouter()
router.register(r'lost', LostProductViewSet, basename='lost')
router.register(r'found', FoundProductViewSet, basename='found')
router.register(r'matches', MatchResultViewSet, basename='matches')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'routes', RouteMapViewSet, basename='routes')

urlpatterns = [
    path('api/ai/', include(router.urls)),
    path('api/ai/recent/', views.recent, name='recent'),
    path('api/ai/report/', views.report, name='report'),
    path('api/ai/notifications/', views.notifications, name='notifications'),
    path('api/ai/match/', views.match, name='match'),
    path('api/ai/route/', views.route, name='route'),
    path('home/', views.home, name='home'),
    path('', views.home, name='home'),
    path('add_found_product/', views.add_found_product, name='add_found_product'),
    path('add_lost_product/', views.add_lost_product, name='add_lost_product'),
    
]
