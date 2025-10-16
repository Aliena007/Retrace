## ========================== views.py ==========================
import io
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import LostProduct, FoundProduct, MatchResult, Notification, RouteMap

try:
    from PIL import Image
    import torch
    import torchvision.transforms as transforms
    import torchvision.models as models
    from torchvision.models import ResNet18_Weights
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# -------------------- Lazy model loading --------------------
_resnet_model = None
_preprocess = None
_device = None

def get_model():
    """Lazy loading of the ResNet model to avoid startup delays."""
    global _resnet_model, _preprocess, _device
    
    if not TORCH_AVAILABLE:
        return None, None, None
    
    if _resnet_model is None:
        try:
            _device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Use a pre-trained ResNet18 for image embeddings
            _resnet_model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
            _resnet_model = torch.nn.Sequential(*list(_resnet_model.children())[:-1])  # Remove final classifier
            _resnet_model = _resnet_model.to(_device)
            _resnet_model.eval()

            # Preprocessing for ResNet
            _preprocess = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                   std=[0.229, 0.224, 0.225])
            ])
        except Exception as e:
            print(f"Failed to load model: {e}")
            return None, None, None
            
    return _resnet_model, _preprocess, _device

# -------------------- Helper functions ------------------------
def generate_embedding(image_field):
    """Convert uploaded image to vector embedding using ResNet18."""
    if not image_field:
        return None
    
    resnet_model, preprocess, device = get_model()
    if resnet_model is None:
        return None
    
    try:
        image = Image.open(image_field).convert("RGB")
        image_tensor = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            embedding = resnet_model(image_tensor)  # shape: [1, 512, 1, 1]
        
        embedding = embedding.squeeze().cpu().numpy()  # shape: [512]
        return embedding.astype(np.float32).tobytes()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def cosine_similarity(vec1, vec2):
    """Cosine similarity between two embeddings."""
    v1 = np.frombuffer(vec1, dtype=np.float32)
    v2 = np.frombuffer(vec2, dtype=np.float32)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# -------------------- Lost Product ----------------------------
def add_lost_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # Create lost product with user if authenticated
        lost_data = {
            'name': name,
            'description': description,
            'image': image,
            'email': email,
            'location': location,
        }
        if request.user.is_authenticated:
            lost_data['user'] = request.user
        
        lost = LostProduct.objects.create(**lost_data)

        # Generate embedding
        lost_embedding = generate_embedding(image)
        
        if lost_embedding is not None:
            # Compare with all found products
            found_products = FoundProduct.objects.all()
            for found in found_products:
                if found.image:
                    found_embedding = generate_embedding(found.image)
                    if found_embedding is not None:
                        similarity = cosine_similarity(lost_embedding, found_embedding)

                        match_status = "Matched" if similarity >= 0.8 else "Not Matched"
                        match = MatchResult.objects.create(
                            lost_product=lost,
                            found_product=found,
                            lost_embedding=lost_embedding,
                            found_embedding=found_embedding,
                            similarity_score=similarity,
                            match_status=match_status,
                        )

                        if match_status == "Matched":
                            send_match_notification(lost, found)

        return redirect("home")  # Redirect to home since lost_detail might not exist

    return render(request, "add_lost_product.html")


# -------------------- Found Product ---------------------------
def add_found_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        email = request.POST.get("email")
        location = request.POST.get("location")

        # Create found product with user if authenticated
        found_data = {
            'name': name,
            'description': description,
            'image': image,
            'email': email,
            'location': location,
        }
        if request.user.is_authenticated:
            found_data['user'] = request.user
        
        found = FoundProduct.objects.create(**found_data)

        # Generate embedding
        found_embedding = generate_embedding(image)

        if found_embedding is not None:
            # Compare with all lost products
            lost_products = LostProduct.objects.all()
            for lost in lost_products:
                if lost.image:
                    lost_embedding = generate_embedding(lost.image)
                    if lost_embedding is not None:
                        similarity = cosine_similarity(lost_embedding, found_embedding)

                        match_status = "Matched" if similarity >= 0.8 else "Not Matched"
                        match = MatchResult.objects.create(
                            lost_product=lost,
                            found_product=found,
                            lost_embedding=lost_embedding,
                            found_embedding=found_embedding,
                            similarity_score=similarity,
                            match_status=match_status,
                        )

                        if match_status == "Matched":
                            send_match_notification(lost, found)

        return redirect("home")  # Redirect to home since found_detail might not exist

    return render(request, "add_found_product.html")


# -------------------- Notification ----------------------------
def send_match_notification(lost, found):
    """Send email notification when a match is found."""
    subject = f"Match Found for {lost.name}!"
    message = (
        f"Good news! Your lost item '{lost.name}' might match with a found item.\n\n"
        f"Found item: {found.name}\n"
        f"Description: {found.description}\n"
        f"Location: {found.location or 'Not specified'}\n"
        f"Contact: {found.email or 'Not provided'}"
    )
    
    # Send email if we have an email and settings are configured
    if lost.email and hasattr(settings, 'DEFAULT_FROM_EMAIL'):
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [lost.email])
        except Exception as e:
            print(f"Failed to send email: {e}")

    # Create notification record
    try:
        notification_data = {
            'message': message,
            'sent_via': "Email",
            'is_sent': True,
        }
        if hasattr(lost, 'user') and lost.user:
            notification_data['user'] = lost.user
        else:
            notification_data['user_contact'] = lost.email or 'Unknown'
            
        Notification.objects.create(**notification_data)
    except Exception as e:
        print(f"Failed to create notification: {e}")


# -------------------- Route Map (Stub) -----------------------
def generate_route(request, lost_id):
    lost = get_object_or_404(LostProduct, pk=lost_id)
    
    route_data = {
        "start": {"lat": lost.latitude, "lng": lost.longitude},
        "end": {"lat": lost.latitude + 0.01, "lng": lost.longitude + 0.01},
        "steps": [
            {"instruction": "Head north 500m"},
            {"instruction": "Turn right at junction"},
            {"instruction": "Arrive at location"},
        ],
    }
    # ===================== Home View =====================
def home(request):
    # You can pass any context, e.g., route_data
    route_data = {}  # or precompute as needed
    return render(request, "Home.html", {"route_data": route_data})

# ===================== Redirect View for Legacy URLs =====================
def redirect_home(request):
    """Handle legacy .html URLs and redirect to proper Django URLs"""
    from django.shortcuts import redirect
    return redirect('home')

# ===================== Form Views =====================
def report_lost_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        location = request.POST.get("location")
        date_lost = request.POST.get("date_lost")

        # Create lost product with user if authenticated
        lost_data = {
            'name': name,
            'description': description,
            'image': image,
            'email': email,
            'phone_number': phone_number,
            'location': location,
        }
        if date_lost:
            lost_data['date_lost'] = date_lost
        if request.user.is_authenticated:
            lost_data['user'] = request.user
        
        lost = LostProduct.objects.create(**lost_data)

        # Generate embedding and check for matches
        lost_embedding = generate_embedding(image)
        matches_found = 0
        
        if lost_embedding is not None:
            # Compare with all found products
            found_products = FoundProduct.objects.all()
            for found in found_products:
                if found.image:
                    found_embedding = generate_embedding(found.image)
                    if found_embedding is not None:
                        similarity = cosine_similarity(lost_embedding, found_embedding)

                        match_status = "Matched" if similarity >= 0.8 else "Not Matched"
                        match = MatchResult.objects.create(
                            lost_product=lost,
                            found_product=found,
                            lost_embedding=lost_embedding,
                            found_embedding=found_embedding,
                            similarity_score=similarity,
                            match_status=match_status,
                        )

                        if match_status == "Matched":
                            matches_found += 1
                            send_match_notification(lost, found)

        # Return success message with match info
        context = {
            'success': True,
            'lost_item': lost,
            'matches_found': matches_found
        }
        return render(request, "Lost_product.html", context)

    return render(request, "Lost_product.html")

def report_found_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        location = request.POST.get("location")
        date_found = request.POST.get("date_found")

        # Create found product with user if authenticated
        found_data = {
            'name': name,
            'description': description,
            'image': image,
            'email': email,
            'phone_number': phone_number,
            'location': location,
        }
        if date_found:
            found_data['date_found'] = date_found
        if request.user.is_authenticated:
            found_data['user'] = request.user
        
        found = FoundProduct.objects.create(**found_data)

        # Generate embedding and check for matches
        found_embedding = generate_embedding(image)
        matches_found = 0

        if found_embedding is not None:
            # Compare with all lost products
            lost_products = LostProduct.objects.all()
            for lost in lost_products:
                if lost.image:
                    lost_embedding = generate_embedding(lost.image)
                    if lost_embedding is not None:
                        similarity = cosine_similarity(lost_embedding, found_embedding)

                        match_status = "Matched" if similarity >= 0.8 else "Not Matched"
                        match = MatchResult.objects.create(
                            lost_product=lost,
                            found_product=found,
                            lost_embedding=lost_embedding,
                            found_embedding=found_embedding,
                            similarity_score=similarity,
                            match_status=match_status,
                        )

                        if match_status == "Matched":
                            matches_found += 1
                            send_match_notification(lost, found)

        # Return success message with match info
        context = {
            'success': True,
            'found_item': found,
            'matches_found': matches_found
        }
        return render(request, "Found_product.html", context)

# ==================== Search Dashboard ====================
def search_items(request):
    """
    Comprehensive search dashboard for lost and found items
    """
    context = {
        'search_performed': False,
        'lost_items': [],
        'found_items': [],
        'matches': [],
        'total_results': 0,
        'search_params': {}
    }
    
    if request.method == 'GET' and (request.GET.get('q') or request.GET.get('category') or request.GET.get('location')):
        context['search_performed'] = True
        
        # Get search parameters
        search_query = request.GET.get('q', '').strip()
        category_filter = request.GET.get('category', '')
        location_filter = request.GET.get('location', '')
        item_type = request.GET.get('type', 'all')  # all, lost, found
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Store search params for template
        context['search_params'] = {
            'q': search_query,
            'category': category_filter,
            'location': location_filter,
            'type': item_type,
            'date_from': date_from,
            'date_to': date_to,
        }
        
        # Base querysets
        lost_items = LostProduct.objects.all()
        found_items = FoundProduct.objects.all()
        
        # Apply text search filter
        if search_query:
            lost_items = lost_items.filter(
                name__icontains=search_query
            ) | lost_items.filter(
                description__icontains=search_query
            )
            found_items = found_items.filter(
                name__icontains=search_query
            ) | found_items.filter(
                description__icontains=search_query
            )
        
        # Apply location filter
        if location_filter:
            lost_items = lost_items.filter(location__icontains=location_filter)
            found_items = found_items.filter(location__icontains=location_filter)
        
        # Apply date filters
        if date_from:
            lost_items = lost_items.filter(date_lost__gte=date_from)
            found_items = found_items.filter(date_found__gte=date_from)
        
        if date_to:
            lost_items = lost_items.filter(date_lost__lte=date_to)
            found_items = found_items.filter(date_found__lte=date_to)
        
        # Apply item type filter
        if item_type == 'lost':
            found_items = FoundProduct.objects.none()
        elif item_type == 'found':
            lost_items = LostProduct.objects.none()
        
        # Order by most recent
        lost_items = lost_items.order_by('-created_at')
        found_items = found_items.order_by('-created_at')
        
        # Get matches for the search results
        matches = MatchResult.objects.filter(
            match_status="Matched"
        ).select_related('lost_product', 'found_product').order_by('-timestamp')
        
        if search_query:
            matches = matches.filter(
                lost_product__name__icontains=search_query
            ) | matches.filter(
                found_product__name__icontains=search_query
            )
        
        context.update({
            'lost_items': lost_items,
            'found_items': found_items,
            'matches': matches,
            'total_results': lost_items.count() + found_items.count(),
        })
    
    # Get all unique locations for filter dropdown
    all_locations = set()
    for item in LostProduct.objects.all():
        if item.location:
            all_locations.add(item.location)
    for item in FoundProduct.objects.all():
        if item.location:
            all_locations.add(item.location)
    
    context['all_locations'] = sorted(list(all_locations))
    
    # Get some stats for the dashboard
    context['stats'] = {
        'total_lost': LostProduct.objects.count(),
        'total_found': FoundProduct.objects.count(),
        'total_matches': MatchResult.objects.filter(match_status="Matched").count(),
        'recent_matches': MatchResult.objects.filter(match_status="Matched").order_by('-timestamp')[:5]
    }
    
    return render(request, "Search_dashboard.html", context)

    return render(request, "Found_product.html")
