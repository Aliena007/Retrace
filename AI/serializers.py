from rest_framework import serializers
from .models import LostProduct, FoundProduct, MatchResult, Notification, RouteMap


class LostProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostProduct
        fields = ['id', 'name', 'description', 'date_lost', 'location_lost', 'contact_info', 'image', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class FoundProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoundProduct
        fields = ['id', 'name', 'description', 'date_found', 'location_found', 'contact_info', 'image', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class MatchResultSerializer(serializers.ModelSerializer):
    lost_product_name = serializers.CharField(source='lost_product.name', read_only=True)
    found_product_name = serializers.CharField(source='found_product.name', read_only=True)
    
    class Meta:
        model = MatchResult
        fields = ['id', 'lost_product', 'found_product', 'lost_product_name', 'found_product_name', 'match_score', 'created_at']
        read_only_fields = ['created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user_contact', 'message', 'sent_at']
        read_only_fields = ['sent_at']


class RouteMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteMap
        fields = ['id', 'lost_product', 'found_product', 'route_data', 'created_at']
        read_only_fields = ['created_at']
