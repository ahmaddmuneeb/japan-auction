# scraper/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarViewSet

router = DefaultRouter()
router.register(r'cars', CarViewSet)

urlpatterns = [
    # Manually add a route to retrieve by stock_id
    path('cars/<str:stock_id>/', CarViewSet.as_view({'get': 'retrieve'}), name='car-detail-by-stock-id'),
    path('', include(router.urls)),
]