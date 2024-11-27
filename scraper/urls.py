# scraper/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarViewSet

router = DefaultRouter()
router.register(r'cars', CarViewSet)

urlpatterns = [
    # Custom route for start_scraping action
    path('cars/start_scraping/', CarViewSet.as_view({'post': 'start_scraping'}), name='start-scraping'),
    path('cars/<str:stock_id>/', CarViewSet.as_view({'get': 'retrieve'}), name='car-detail-by-stock-id'),
    path('', include(router.urls)),
]
