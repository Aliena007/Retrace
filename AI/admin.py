from django.contrib import admin
from .models import AImodels  # Replace 'YourModel' with the actual name of your Django model class

# Register your models here.
admin.site.register(AImodels)
from django.contrib import admin
from .models import LostProduct, FoundProduct, MatchResult, Notification, RouteMap

admin.site.register(LostProduct)
admin.site.register(FoundProduct)
admin.site.register(MatchResult)
admin.site.register(Notification)
admin.site.register(RouteMap)
