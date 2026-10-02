// Profile Feature JavaScript
document.addEventListener("DOMContentLoaded", function() {
  const avatarPreview = document.getElementById("avatar-preview");
  const avatarImg = document.getElementById("avatar-preview-img");
  const nicknameInput = document.getElementById("id_nickname");
  const colorRadios = document.querySelectorAll("input[name='avatar_color']");
  const fileInput = document.getElementById("id_profile_image");
  const removeImageCheckbox = document.getElementById("remove_image");

  // Live update avatar letter from nickname
  if (nicknameInput && avatarPreview) {
    nicknameInput.addEventListener("input", function() {
      const val = this.value.trim();
      avatarPreview.textContent = val ? val[0].toUpperCase() : "A";
    });
  }

  // Live update avatar swatch color
  if (avatarPreview && colorRadios) {
    colorRadios.forEach(radio => {
      radio.addEventListener("change", function() {
        if (this.checked) {
          avatarPreview.style.backgroundColor = this.value;
        }
      });
    });
  }

  // Live preview for profile image upload
  if (fileInput) {
    fileInput.addEventListener("change", function() {
      const file = this.files && this.files[0];
      if (file) {
        if (!file.type.startsWith("image/")) {
          alert("Please choose a valid image file (PNG, JPG, JPEG, WEBP).");
          fileInput.value = "";
          return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
          if (avatarImg) {
            avatarImg.src = e.target.result;
            avatarImg.style.display = "block";
          }
          if (avatarPreview) {
            avatarPreview.style.display = "none";
          }
          if (removeImageCheckbox) {
            removeImageCheckbox.checked = false;
          }
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Handle remove photo toggle
  if (removeImageCheckbox) {
    removeImageCheckbox.addEventListener("change", function() {
      if (this.checked) {
        if (avatarImg) avatarImg.style.display = "none";
        if (avatarPreview) avatarPreview.style.display = "grid";
        if (fileInput) fileInput.value = "";
      } else {
        const originalSrc = avatarImg ? avatarImg.getAttribute("data-original-src") : null;
        if (originalSrc) {
          avatarImg.src = originalSrc;
          avatarImg.style.display = "block";
          if (avatarPreview) avatarPreview.style.display = "none";
        }
      }
    });
  }
});
