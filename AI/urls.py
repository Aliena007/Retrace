<<<<<<< HEAD
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import LostProductViewSet, FoundProductViewSet, MatchResultViewSet, NotificationViewSet, RouteMapViewSet

router = DefaultRouter()
router.register(r'lost', LostProductViewSet, basename='lost')
router.register(r'found', FoundProductViewSet, basename='found')
router.register(r'matches', MatchResultViewSet, basename='matches')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'routes', RouteMapViewSet, basename='routes')

urlpatterns = [
    path('api/ai/', include(router.urls)),
    path('home/', views.home, name='home'),
    path('', views.home, name='home'),
    path('search/', views.search_items, name='search_items'),
    path('report-lost/', views.report_lost_product, name='report_lost'),
    path('report-found/', views.report_found_product, name='report_found'),
    path('add_found_product/', views.add_found_product, name='add_found_product'),
    path('add_lost_product/', views.add_lost_product, name='add_lost_product'),
]
=======
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import LostProductViewSet, FoundProductViewSet, MatchResultViewSet, NotificationViewSet, RouteMapViewSet

router = DefaultRouter()
router.register(r'lost', LostProductViewSet, basename='lost')
router.register(r'found', FoundProductViewSet, basename='found')
router.register(r'matches', MatchResultViewSet, basename='matches')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'routes', RouteMapViewSet, basename='routes')

urlpatterns = [
    path('api/ai/', include(router.urls)),
    path('home/', views.home, name='home'),
    path('', views.home, name='home'),
    path('add_found_product/', views.add_found_product, name='add_found_product'),
    path('add_lost_product/', views.add_lost_product, name='add_lost_product'),
    
]
>>>>>>> 8b1e1d938e70917f9e7bc0a124a56dd9f9496b7e
