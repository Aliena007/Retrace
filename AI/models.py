from django.db import models

# Create your models here.
class AImodels(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
route_data = models.JSONField(blank=True, null=True)
route_data = models.JSONField(blank=True, null=True)
route_data = models.JSONField(blank=True, null=True)
route_data = models.JSONField(blank=True, null=True)
route_data = models.JSONField(blank=True, null=True)
route_data = models.JSONField(blank=True, null=True)

def __str__(self):
        return self.name
class LostProduct(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_lost = models.DateField()
    location_lost = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    image = models.ImageField(upload_to='lost_products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name        
class FoundProduct(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_found = models.DateField()
    location_found = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    image = models.ImageField(upload_to='found_products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
class MatchResult(models.Model):
    id = models.AutoField(primary_key=True)
    lost_product = models.ForeignKey(LostProduct, on_delete=models.CASCADE)
    found_product = models.ForeignKey(FoundProduct, on_delete=models.CASCADE)
    match_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match {self.id}: {self.lost_product.name} - {self.found_product.name}"
class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user_contact = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification {self.id} to {self.user_contact}"
class RouteMap(models.Model):
    id = models.AutoField(primary_key=True)
    lost_product = models.ForeignKey(LostProduct, on_delete=models.CASCADE)
    found_product = models.ForeignKey(FoundProduct, on_delete=models.CASCADE)
    route_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RouteMap {self.id} for {self.lost_product.name} to {self.found_product.name}"
