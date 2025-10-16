## ========================== views.py ==========================
"""AI app views - cleaned and merged.

This module contains Django views for reporting lost/found items, matching using
an optional ResNet18 embedding model, notification creation, and simple search
and routing helpers.
"""

import io
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

from .models import LostProduct, FoundProduct, MatchResult, Notification, RouteMap


# Try to import torch and torchvision; code should continue working if not installed.
try:
    from PIL import Image
except Exception:
    Image = None

try:
    import torch
    import torchvision.transforms as transforms
    import torchvision.models as models
    from torchvision.models import ResNet18_Weights
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


# -------------------- Lazy model loading --------------------
_resnet_model = None
_preprocess = None
_device = None


def get_model():
    """Return (model, preprocess, device) or (None, None, None) if torch not present."""
    global _resnet_model, _preprocess, _device
    if not TORCH_AVAILABLE:
        return None, None, None
    if _resnet_model is None:
        try:
            _device = "cuda" if torch.cuda.is_available() else "cpu"
            _resnet_model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
            _resnet_model = torch.nn.Sequential(*list(_resnet_model.children())[:-1])
            _resnet_model = _resnet_model.to(_device)
            _resnet_model.eval()
            _preprocess = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
        except Exception as e:
            print(f"Failed to load model: {e}")
            return None, None, None
    return _resnet_model, _preprocess, _device


def generate_embedding(image_field):
    """Convert uploaded image to vector embedding using ResNet18.

    Returns raw bytes of float32 vector or None on failure / when model unavailable.
    """
    if not image_field or not TORCH_AVAILABLE or Image is None:
        return None
    model, preprocess, device = get_model()
    if model is None or preprocess is None:
        return None
    try:
        image = Image.open(image_field).convert("RGB")
        tensor = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            emb = model(tensor)
        emb = emb.squeeze().cpu().numpy()
        return emb.astype(np.float32).tobytes()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def cosine_similarity(vec1, vec2):
    v1 = np.frombuffer(vec1, dtype=np.float32)
    v2 = np.frombuffer(vec2, dtype=np.float32)
    denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
    if denom == 0:
        return 0.0
    return float(np.dot(v1, v2) / denom)


def add_lost_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        email = request.POST.get("email")
        location = request.POST.get("location")

        lost_data = {'name': name, 'description': description, 'image': image, 'email': email, 'location': location}
        if request.user.is_authenticated:
            lost_data['user'] = request.user
        lost = LostProduct.objects.create(**lost_data)

        lost_emb = generate_embedding(image)
        if lost_emb is not None:
            for found in FoundProduct.objects.all():
                if found.image:
                    found_emb = generate_embedding(found.image)
                    if found_emb is not None:
                        sim = cosine_similarity(lost_emb, found_emb)
                        status = "Matched" if sim >= 0.8 else "Not Matched"
                        MatchResult.objects.create(
                            lost_product=lost,
                            found_product=found,
                            lost_embedding=lost_emb,
                            found_embedding=found_emb,
                            similarity_score=sim,
                            match_status=status,
                        )
                        if status == "Matched":
                            send_match_notification(lost, found)
        return redirect('home')
    return render(request, "add_lost_product.html")


def add_found_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        email = request.POST.get("email")
        location = request.POST.get("location")

        found_data = {'name': name, 'description': description, 'image': image, 'email': email, 'location': location}
        if request.user.is_authenticated:
            found_data['user'] = request.user
        found = FoundProduct.objects.create(**found_data)

        found_emb = generate_embedding(image)
        if found_emb is not None:
            for lost in LostProduct.objects.all():
                if lost.image:
                    lost_emb = generate_embedding(lost.image)
                    if lost_emb is not None:
                        sim = cosine_similarity(lost_emb, found_emb)
                        status = "Matched" if sim >= 0.8 else "Not Matched"
                        MatchResult.objects.create(
                            lost_product=lost,
                            found_product=found,
                            lost_embedding=lost_emb,
                            found_embedding=found_emb,
                            similarity_score=sim,
                            match_status=status,
                        )
                        if status == "Matched":
                            send_match_notification(lost, found)
        return redirect('home')
    return render(request, "add_found_product.html")


def send_match_notification(lost, found):
    subject = f"Match Found for {lost.name}!"
    message = (
        f"Good news! Your lost item '{lost.name}' might match with a found item.\n\n"
        f"Found item: {found.name}\n"
        f"Description: {found.description}\n"
        f"Location: {getattr(found, 'location', 'Not specified')}\n"
        f"Contact: {getattr(found, 'email', 'Not provided')}"
    )
    recipient = getattr(lost, 'email', None)
    if recipient and getattr(settings, 'DEFAULT_FROM_EMAIL', None):
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
        except Exception as e:
            print(f"Failed to send email: {e}")
    try:
        Notification.objects.create(
            user=getattr(lost, 'user', None),
            user_contact=getattr(lost, 'email', None),
            message=message,
            sent_via='Email',
            is_sent=bool(recipient),
        )
    except Exception as e:
        print(f"Failed to create notification: {e}")


def generate_route(request, lost_id):
    lost = get_object_or_404(LostProduct, pk=lost_id)
    route_data = {
        "start": {"lat": getattr(lost, 'latitude', 0), "lng": getattr(lost, 'longitude', 0)},
        "end": {"lat": (getattr(lost, 'latitude', 0)) + 0.01, "lng": (getattr(lost, 'longitude', 0)) + 0.01},
        "steps": [{"instruction": "Head north 500m"}, {"instruction": "Turn right at junction"}, {"instruction": "Arrive at location"}],
    }
    return JsonResponse(route_data, safe=False)


def home(request):
    return render(request, "Home.html", {"route_data": {}})


def redirect_home(request):
    from django.shortcuts import redirect

    return redirect('home')


def report_lost_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        location = request.POST.get('location')
        date_lost = request.POST.get('date_lost')
        data = {'name': name, 'description': description, 'image': image, 'email': email, 'phone_number': phone_number, 'location': location}
        if date_lost:
            data['date_lost'] = date_lost
        if request.user.is_authenticated:
            data['user'] = request.user
        lost = LostProduct.objects.create(**data)
        lost_emb = generate_embedding(image)
        matches_found = 0
        if lost_emb is not None:
            for found in FoundProduct.objects.all():
                if found.image:
                    found_emb = generate_embedding(found.image)
                    if found_emb is not None:
                        sim = cosine_similarity(lost_emb, found_emb)
                        status = 'Matched' if sim >= 0.8 else 'Not Matched'
                        MatchResult.objects.create(lost_product=lost, found_product=found, lost_embedding=lost_emb, found_embedding=found_emb, similarity_score=sim, match_status=status)
                        if status == 'Matched':
                            matches_found += 1
                            send_match_notification(lost, found)
        return render(request, 'Lost_product.html', {'success': True, 'lost_item': lost, 'matches_found': matches_found})
    return render(request, 'Lost_product.html')


def report_found_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        location = request.POST.get('location')
        date_found = request.POST.get('date_found')
        data = {'name': name, 'description': description, 'image': image, 'email': email, 'phone_number': phone_number, 'location': location}
        if date_found:
            data['date_found'] = date_found
        if request.user.is_authenticated:
            data['user'] = request.user
        found = FoundProduct.objects.create(**data)
        found_emb = generate_embedding(image)
        matches_found = 0
        if found_emb is not None:
            for lost in LostProduct.objects.all():
                if lost.image:
                    lost_emb = generate_embedding(lost.image)
                    if lost_emb is not None:
                        sim = cosine_similarity(lost_emb, found_emb)
                        status = 'Matched' if sim >= 0.8 else 'Not Matched'
                        MatchResult.objects.create(lost_product=lost, found_product=found, lost_embedding=lost_emb, found_embedding=found_emb, similarity_score=sim, match_status=status)
                        if status == 'Matched':
                            matches_found += 1
                            send_match_notification(lost, found)
        return render(request, 'Found_product.html', {'success': True, 'found_item': found, 'matches_found': matches_found})
    return render(request, 'Found_product.html')


def search_items(request):
    context = {'search_performed': False, 'lost_items': [], 'found_items': [], 'matches': [], 'total_results': 0, 'search_params': {}}
    if request.method == 'GET' and (request.GET.get('q') or request.GET.get('category') or request.GET.get('location')):
        context['search_performed'] = True
        search_query = request.GET.get('q', '').strip()
        location_filter = request.GET.get('location', '')
        item_type = request.GET.get('type', 'all')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        context['search_params'] = {'q': search_query, 'location': location_filter, 'type': item_type, 'date_from': date_from, 'date_to': date_to}
        lost_items = LostProduct.objects.all()
        found_items = FoundProduct.objects.all()
        if search_query:
            lost_items = lost_items.filter(name__icontains=search_query) | lost_items.filter(description__icontains=search_query)
            found_items = found_items.filter(name__icontains=search_query) | found_items.filter(description__icontains=search_query)
        if location_filter:
            lost_items = lost_items.filter(location__icontains=location_filter)
            found_items = found_items.filter(location__icontains=location_filter)
        if date_from:
            lost_items = lost_items.filter(date_lost__gte=date_from)
            found_items = found_items.filter(date_found__gte=date_from)
        if date_to:
            lost_items = lost_items.filter(date_lost__lte=date_to)
            found_items = found_items.filter(date_found__lte=date_to)
        if item_type == 'lost':
            found_items = FoundProduct.objects.none()
        elif item_type == 'found':
            lost_items = LostProduct.objects.none()
        lost_items = lost_items.order_by('-created_at')
        found_items = found_items.order_by('-created_at')
        matches = MatchResult.objects.filter(match_status='Matched').select_related('lost_product', 'found_product').order_by('-created_at')
        if search_query:
            matches = matches.filter(lost_product__name__icontains=search_query) | matches.filter(found_product__name__icontains=search_query)
        context.update({'lost_items': lost_items, 'found_items': found_items, 'matches': matches, 'total_results': lost_items.count() + found_items.count()})
    all_locations = set()
    for item in LostProduct.objects.all():
        if getattr(item, 'location', None):
            all_locations.add(item.location)
    for item in FoundProduct.objects.all():
        if getattr(item, 'location', None):
            all_locations.add(item.location)
    context['all_locations'] = sorted(list(all_locations))
    context['stats'] = {
        'total_lost': LostProduct.objects.count(),
        'total_found': FoundProduct.objects.count(),
        'total_matches': MatchResult.objects.filter(match_status='Matched').count(),
    'recent_matches': MatchResult.objects.filter(match_status='Matched').order_by('-created_at')[:5],
    }
    return render(request, "Search_dashboard.html", context)
