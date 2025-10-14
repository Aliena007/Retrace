from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.conf import settings

# Create your models here.
class Product(models.Model):
    LIVE=1
    INACTIVE=0
    DELETE_CHOICES = [
        (LIVE, 'Live'),(INACTIVE, 'Inactive'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(choices=[('Electronics', 'Electronics'), ('Clothing', 'Clothing'), ('Stationery', 'Stationery'), ('Other', 'Other')], max_length=50)
    status = models.CharField(choices=[('Lost', 'Lost'), ('Found', 'Found')], max_length=10)
    location = models.CharField(max_length=255)
    date_reported = models.DateTimeField()
    deleted_status = models.IntegerField(choices=DELETE_CHOICES, default=LIVE)
    image = models.ImageField(upload_to='media/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ['-created_at']  
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Image for {self.product.name}"
    
    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['-uploaded_at']

class LostProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='lost_reports')
    reporter_name = models.CharField(max_length=100)
    reporter_contact = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, blank=True, null=True)
    image = models.ImageField(upload_to='lost_product_images/', null=True, blank=True)
    report_date = models.DateTimeField(auto_now_add=True)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Lost Report for {self.product.name} by {self.reporter_name}"
    
    class Meta:
        verbose_name = 'Product Lost Report'
        verbose_name_plural = 'Product Lost Reports'
        ordering = ['-report_date']
        
class FoundProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='found_reports')
    reporter_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, blank=True, null=True)
    image = models.ImageField(upload_to='found_product_images/', null=True, blank=True)
    reporter_contact = models.CharField(max_length=100)
    report_date = models.DateTimeField(auto_now_add=True)
    additional_info = models.TextField(blank=True, null=True)


    def __str__(self) -> str:
        return f"Found Report for {self.product.name} by {self.reporter_name}"
    
    class Meta:
        verbose_name = 'Product Found Report'
        verbose_name_plural = 'Product Found Reports'
        ordering = ['-report_date']

class MatchResult(models.Model):
    lost_product = models.ForeignKey(LostProduct, on_delete=models.CASCADE, related_name='match_results')
    found_product = models.ForeignKey(FoundProduct, on_delete=models.CASCADE, related_name='match_results')
    lost_embedding = models.BinaryField(null=True, blank=True)
    found_embedding = models.BinaryField(null=True, blank=True)
    similarity_score = models.FloatField()
    match_status = models.CharField(max_length=50)  # e.g., "Matched", "Not Matched"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"MatchResult: {self.lost_product} <-> {self.found_product} ({self.similarity_score})"
    
    class Meta:
        verbose_name = 'Product Match Result'
        verbose_name_plural = 'Product Match Results'
        ordering = ['-created_at']
class Notification(models.Model):
    user = models.CharField(max_length=100)  # In a real app, this would be a ForeignKey to a User model
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Notification for {self.user}: {self.message[:20]}..."
    
    class Meta:
        verbose_name = 'Product Notification'
        verbose_name_plural = 'Product Notifications'
        ordering = ['-created_at']
class RouteMap(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='route_maps')
    map_image = models.ImageField(upload_to='route_maps/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"RouteMap for {self.product.name}"
    
    class Meta:
        verbose_name = 'Product Route Map'
        verbose_name_plural = 'Product Route Maps'
        ordering = ['-created_at']
