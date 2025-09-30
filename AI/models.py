from django.db import models

# Define lost_Product and found_Product models first
class lost_Product(models.Model):
    # Add fields as needed
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='lost_product_images/', null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True, null=True)

class found_Product(models.Model):
    # Add fields as needed
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='found_product_images/', null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True, null=True)

# Create your models here.
class ExampleModel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    lost_Product = models.ForeignKey(lost_Product, on_delete=models.CASCADE)
    found_Product = models.ForeignKey(found_Product, on_delete=models.CASCADE)
    lost_embedding = models.BinaryField()   # store vector as binary/JSON
    found_embedding = models.BinaryField()
    similarity_score = models.FloatField()
    threshold_used = models.FloatField(default=0.8)
    match_status = models.CharField(max_length=20, choices=[("Matched","Matched"),("Not Matched","Not Matched")])
    notified_users = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)    

    def __str__(self) -> str:
        return self.name