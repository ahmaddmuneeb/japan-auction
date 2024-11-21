# scraper/serializers.py
from rest_framework import serializers
from .models import Car, CarImage

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['image_url']

class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'stock_id', 'car_brand_name', 'car_name', 'car_year',
                 'price', 'total_price', 'distance', 'fuel', 'body_color',
                 'location', 'created_at', 'updated_at', 'images']