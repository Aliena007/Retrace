import email
from email.mime import image
from os import name
from django.http import HttpResponse
from django.shortcuts import render
from .models import Notification,RouteMap,MatchResult,FoundProduct,LostProduct,ProductImage,Product

# Create your views here.
def report_lost(request):
    name = request.POST.get("Product name")
    description = request.POST.get("Description")
    category = request.POST.get("Category")
    status = request.POST.get("Status")
    image = request.FILES.get("Image")
    location = request.POST.get("Location")
    date_reported = request.POST.get("Date Reported")
    reporter_name = request.POST.get("Reporter Name")
    reporter_contact = request.POST.get("Reporter Contact")
    email = request.POST.get("Email")
    additional_info = request.POST.get("Additional Info")
    if name and description and category and status and location and date_reported and reporter_name and reporter_contact:
        # Save the lost product report to the database
        return HttpResponse("Lost product reported successfully.")
    else:
        return render(request, 'Lost_product.html', {'error': 'Please fill in all required fields.'})
        return render(request, 'Lost_product.html')
    a=LostProduct(name=name, description=description,status=status,category=category,image=image, location=location,date_reported=date_reported,reporter_contact=reporter_contact,email=email)
    a.save()
def report_found(request):
    name = request.POST.get("Product name")
    description = request.POST.get("Description")
    category = request.POST.get("Category")
    status = request.POST.get("Status")
    image = request.FILES.get("Image")
    location = request.POST.get("Location")
    date_reported = request.POST.get("Date Reported")
    reporter_name = request.POST.get("Reporter Name")
    reporter_contact = request.POST.get("Reporter Contact")
    email = request.POST.get("Email")
    additional_info = request.POST.get("Additional Info")
    if name and description and category and status and location and date_reported and reporter_name and reporter_contact:
        # Save the found product report to the database
        return HttpResponse("Found product reported successfully.")
    else:
        return render(request, 'Found_product.html', {'error': 'Please fill in all required fields.'})
        return render(request, 'Found_product.html') 
    b=FoundProduct(name=name, description=description,status=status,category=category,image=image, location=location,date_reported=date_reported,reporter_contact=reporter_contact,email=email)
    b.save()
def Product(request):
    return render(request, 'Dashboard.html', {'style': 'Style.css'})

