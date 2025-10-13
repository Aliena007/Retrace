## ========================== views.py ==========================
import io
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import LostProduct, FoundProduct, MatchResult, Notification, RouteMap

from PIL import Image
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from torchvision.models import ResNet18_Weights

# -------------------- Setup model (CPU/GPU) --------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

# Use a pre-trained ResNet18 for image embeddings
resnet_model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
resnet_model = torch.nn.Sequential(*list(resnet_model.children())[:-1])  # Remove final classifier
resnet_model = resnet_model.to(device)
resnet_model.eval()

# Preprocessing for ResNet
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# -------------------- Helper functions ------------------------
def generate_embedding(image_field):
    """Convert uploaded image to vector embedding using ResNet18."""
    if not image_field:
        return None
    
    image = Image.open(image_field).convert("RGB")
    image_tensor = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = resnet_model(image_tensor)  # shape: [1, 512, 1, 1]
    
    embedding = embedding.squeeze().cpu().numpy()  # shape: [512]
    return embedding.astype(np.float32).tobytes()


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

        lost = LostProduct.objects.create(
            user=request.user,
            name=name,
            description=description,
            image=image,
            email=email,
            location=location,
        )

        # Generate embedding
        lost_embedding = generate_embedding(image)
        
        # Compare with all found products
        found_products = FoundProduct.objects.all()
        for found in found_products:
            if found.image:
                found_embedding = generate_embedding(found.image)
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

        return redirect("lost_detail", pk=lost.pk)

    return render(request, "add_lost_product.html")


# -------------------- Found Product ---------------------------
def add_found_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        email = request.POST.get("email")
        location = request.POST.get("location")

        found = FoundProduct.objects.create(
            user=request.user,
            name=name,
            description=description,
            image=image,
            email=email,
            location=location,
        )

        # Generate embedding
        found_embedding = generate_embedding(image)

        # Compare with all lost products
        lost_products = LostProduct.objects.all()
        for lost in lost_products:
            if lost.image:
                lost_embedding = generate_embedding(lost.image)
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

        return redirect("found_detail", pk=found.pk)

    return render(request, "add_found_product.html")


# -------------------- Notification ----------------------------
def send_match_notification(lost, found):
    """Send email notification when a match is found."""
    subject = f"Match Found for {lost.name}!"
    message = (
        f"Good news! Your lost item '{lost.name}' might match with a found item.\n\n"
        f"Found item: {found.name}\n"
        f"Description: {found.description}\n"
        f"Location: {found.location}\n"
        f"Contact: {found.email}"
    )
    recipient = lost.email

    if recipient:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
        Notification.objects.create(
            user=lost.user,
            message=message,
            sent_via="Email",
            is_sent=True,
        )


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
from django.shortcuts import render

def home(request):
    # You can pass any context, e.g., route_data
    route_data = {}  # or precompute as needed
    return render(request, "home.html", {"route_data": route_data})

    return JsonResponse(route_data, safe=False)
