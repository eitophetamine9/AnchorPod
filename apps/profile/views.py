import io
import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from PIL import Image, ImageOps
from .models import Profile


def process_profile_image(uploaded_file, max_size=400):
    """
    Validates, auto-orients, crops to center square, downscales to max_size,
    and returns a standardized ContentFile.
    """
    image = Image.open(uploaded_file)

    # Auto-orient based on EXIF
    image = ImageOps.exif_transpose(image)

    # Crop to square from center
    width, height = image.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    image = image.crop((left, top, right, bottom))

    # Downscale if larger than max_size
    if min_dim > max_size:
        image = image.resize((max_size, max_size), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    filename_base, ext = os.path.splitext(uploaded_file.name)
    ext = ext.lower()

    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        image.save(buffer, format='PNG', optimize=True)
        file_ext = '.png'
    else:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(buffer, format='JPEG', quality=85, optimize=True)
        file_ext = '.jpg'

    buffer.seek(0)
    clean_name = f"{filename_base[:24]}_avatar{file_ext}"
    return ContentFile(buffer.getvalue(), name=clean_name)


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'nickname': f"Anchor {request.user.username[:1].upper() or 'A'}",
            'goals': ['Drink water', 'Step outside', 'Study for 25 minutes'],
        }
    )

    if request.method == "POST":
        nickname = request.POST.get("nickname", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        bio = request.POST.get("bio", "").strip()
        avatar_color = request.POST.get("avatar_color", profile.avatar_color).strip()
        goals_raw = request.POST.get("goals", "")

        profile.nickname = nickname or profile.nickname
        profile.full_name = full_name
        profile.bio = bio
        profile.avatar_color = avatar_color

        if goals_raw:
            # Parse line-delimited or comma-delimited goals
            goals = [g.strip() for g in goals_raw.replace("\r", "").split("\n") if g.strip()]
            profile.goals = goals

        # Handle profile picture upload or removal
        if request.POST.get("remove_image") == "on":
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            profile.profile_image = None
        elif "profile_image" in request.FILES:
            raw_file = request.FILES["profile_image"]
            if raw_file.size > 10 * 1024 * 1024:
                messages.error(request, "The uploaded image exceeds 10MB. Please choose a smaller file.")
                return redirect("profile:profile")
            try:
                processed_image = process_profile_image(raw_file)
                if profile.profile_image:
                    profile.profile_image.delete(save=False)
                profile.profile_image = processed_image
            except Exception:
                messages.error(request, "Could not process this image. Please upload a valid PNG, JPG, or WEBP.")
                return redirect("profile:profile")

        profile.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profile:profile")

    goals_text = "\n".join(profile.goals) if profile.goals else ""
    return render(request, "profile/profile.html", {
        "profile": profile,
        "goals_text": goals_text,
    })

