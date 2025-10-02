from django.db import models
from django.contrib.auth.models import User

class LostProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lost_items")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="lost_product_images/", null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # last seen location
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lost: {self.name} ({self.user.username})"

class FoundProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="found_items")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="found_product_images/", null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # found location
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Found: {self.name} ({self.user.username})"

class MatchResult(models.Model):
    lost_product = models.ForeignKey(LostProduct, on_delete=models.CASCADE)
    found_product = models.ForeignKey(FoundProduct, on_delete=models.CASCADE)
    lost_embedding = models.BinaryField()   # store vector embeddings for AI image comparison
    found_embedding = models.BinaryField()
    similarity_score = models.FloatField()
    threshold_used = models.FloatField(default=0.8)
    match_status = models.CharField(
        max_length=20,
        choices=[("Matched", "Matched"), ("Not Matched", "Not Matched")],
    )
    notified_users = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match: {self.lost_product.name} ↔ {self.found_product.name} [{self.match_status}]"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sent_via = models.CharField(
        max_length=20,
        choices=[("Email", "Email"), ("SMS", "SMS"), ("WhatsApp", "WhatsApp")]
    )
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.user.username} ({self.sent_via})"

class RouteMap(models.Model):
    product = models.ForeignKey(LostProduct, on_delete=models.CASCADE, related_name="routes")
    route_data = models.JSONField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Route Map for {self.product.name}"
