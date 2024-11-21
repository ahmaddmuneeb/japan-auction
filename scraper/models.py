# scraper/models.py
from django.db import models

class Car(models.Model):
    stock_id = models.CharField(max_length=200, unique=True)
    car_brand_name = models.CharField(max_length=100)
    car_name = models.CharField(max_length=200)
    car_year = models.CharField(max_length=4)
    price = models.CharField(max_length=100)
    total_price = models.CharField(max_length=100)
    distance = models.CharField(max_length=100)
    fuel = models.CharField(max_length=50)
    body_color = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField()

# # scraper/serializers.py
# from rest_framework import serializers
# from .models import Car, CarImage

# class CarImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CarImage
#         fields = ['image_url']

# class CarSerializer(serializers.ModelSerializer):
#     images = CarImageSerializer(many=True, read_only=True)

#     class Meta:
#         model = Car
#         fields = ['id', 'stock_id', 'car_brand_name', 'car_name', 'car_year',
#                  'price', 'total_price', 'distance', 'fuel', 'body_color',
#                  'location', 'created_at', 'updated_at', 'images']
