from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib import messages

from .models import Location, LocationLog, LocationSettings, LocationReport


# -------------------------------
# List all locations
# -------------------------------
def location_list(request):
    locations = Location.objects.all()
    return render(request, "locations/location_list.html", {"locations": locations})


# -------------------------------
# Location Detail with reports & settings
# -------------------------------
def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk)
    reports = location.reports.all()
    settings = getattr(location, "settings", None)
    logs = location.logs.all()[:10]  # show last 10 logs

    return render(request, "locations/location_detail.html", {
        "location": location,
        "reports": reports,
        "settings": settings,
        "logs": logs,
    })


# -------------------------------
# Create a new location
# -------------------------------
def location_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        location = Location.objects.create(name=name, description=description)

        # Log the action
        LocationLog.objects.create(location=location, action="Location created")

        messages.success(request, f"Location '{name}' created successfully!")
        return redirect("location_list")

    return render(request, "locations/location_form.html")


# -------------------------------
# Update a location
# -------------------------------
def location_update(request, pk):
    location = get_object_or_404(Location, pk=pk)

    if request.method == "POST":
        location.name = request.POST.get("name")
        location.description = request.POST.get("description")
        location.save()

        # Log the action
        LocationLog.objects.create(location=location, action="Location updated")

        messages.success(request, f"Location '{location.name}' updated successfully!")
        return redirect("location_detail", pk=pk)

    return render(request, "locations/location_form.html", {"location": location})


# -------------------------------
# Delete a location
# -------------------------------
def location_delete(request, pk):
    location = get_object_or_404(Location, pk=pk)
    name = location.name

    if request.method == "POST":
        location.delete()
        messages.warning(request, f"Location '{name}' deleted successfully!")
        return redirect("location_list")

    return render(request, "locations/location_confirm_delete.html", {"location": location})


# -------------------------------
# Manage Location Settings
# -------------------------------
def location_settings(request, pk):
    location = get_object_or_404(Location, pk=pk)
    settings, created = LocationSettings.objects.get_or_create(location=location)

    if request.method == "POST":
        settings.notifications_enabled = bool(request.POST.get("notifications_enabled"))
        settings.alert_threshold = request.POST.get("alert_threshold") or settings.alert_threshold
        settings.save()

        # Log the action
        LocationLog.objects.create(location=location, action="Settings updated")

        messages.success(request, "Settings updated successfully!")
        return redirect("location_detail", pk=pk)

    return render(request, "locations/location_settings.html", {"location": location, "settings": settings})


# -------------------------------
# Submit a report for a location
# -------------------------------
def submit_report(request, pk):
    location = get_object_or_404(Location, pk=pk)

    if request.method == "POST":
        reporter_name = request.POST.get("reporter_name")
        reporter_contact = request.POST.get("reporter_contact")
        description = request.POST.get("description")

        LocationReport.objects.create(
            location=location,
            reporter_name=reporter_name,
            reporter_contact=reporter_contact,
            description=description,
        )

        # Log the action
        LocationLog.objects.create(location=location, action="Report submitted")

        messages.success(request, "Report submitted successfully!")
        return redirect("location_detail", pk=pk)

    return render(request, "locations/report_form.html", {"location": location})


# -------------------------------
# API Endpoint: Recent Logs for AJAX
# -------------------------------
def get_logs(request, pk):
    location = get_object_or_404(Location, pk=pk)
    logs = location.logs.values("action", "timestamp", "ip_address")[:10]
    return JsonResponse(list(logs), safe=False)

