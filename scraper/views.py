from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .models import Car
from .serializers import CarSerializer
from .tasks import scrape_cars
# from car_scraper.celery import start_periodic_scraping

class CustomCarPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class CarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Car.objects.all().order_by('-created_at')
    serializer_class = CarSerializer
    pagination_class = CustomCarPagination
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    
    filterset_fields = {
        'car_brand_name': ['exact', 'icontains'],
        'car_name': ['exact', 'icontains'],
        'car_year': ['exact', 'gte', 'lte'],
        'price': ['exact', 'gte', 'lte'],
        'total_price': ['exact', 'gte', 'lte'],
        'distance': ['exact', 'gte', 'lte'],
        'fuel': ['exact', 'icontains'],
        'body_color': ['exact', 'icontains'],
        'location': ['exact', 'icontains'],
        'created_at': ['gte', 'lte']
    }
    
    search_fields = [
        'car_brand_name',
        'car_name',
        'location',
        'fuel',
        'body_color'
    ]
    
    ordering_fields = [
        'car_year',
        'price',
        'total_price',
        'distance',
        'created_at'
    ]

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply filters based on parameters
        brand = request.query_params.get('brand')
        min_year = request.query_params.get('min_year')
        max_year = request.query_params.get('max_year')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        fuel_type = request.query_params.get('fuel_type')
        location = request.query_params.get('location')
        color = request.query_params.get('color')
        
        if brand:
            queryset = queryset.filter(car_brand_name__icontains=brand)
        if min_year and max_year:
            queryset = queryset.filter(car_year__gte=min_year, car_year__lte=max_year)
        if min_price and max_price:
            queryset = queryset.filter(price__gte=min_price, price__lte=max_price)
        if fuel_type:
            queryset = queryset.filter(fuel__icontains=fuel_type)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if color:
            queryset = queryset.filter(body_color__icontains=color)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def start_scraping(self, request):
        try:
            # Run immediate scraping task
            scrape_cars.delay()
            
            # Start periodic scheduling
            # start_periodic_scraping()
            
            return Response(
                {"message": "Scraping started and scheduled to run every minute."},
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to start scraping: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )