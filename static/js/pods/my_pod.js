/**
 * AnchorPod - Dedicated "My Pod" Screen Interactivity
 */

document.addEventListener("DOMContentLoaded", function() {
  const nudgeModal = document.getElementById("nudge-modal");
  const closeNudgeBtn = document.getElementById("close-nudge-modal");
  const cancelNudgeBtn = document.getElementById("cancel-nudge-btn");
  const recipientInput = document.getElementById("nudge-recipient-input");
  const targetNameEl = document.getElementById("nudge-target-name");
  const nudgeForm = document.getElementById("nudge-form");

  // Open Nudge Modal
  document.querySelectorAll(".open-nudge-modal-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const recipientId = btn.getAttribute("data-recipient-id");
      const recipientName = btn.getAttribute("data-recipient-name");

      if (recipientInput) recipientInput.value = recipientId;
      if (targetNameEl) targetNameEl.textContent = recipientName || "your peer";

      if (nudgeModal && typeof nudgeModal.showModal === "function") {
        nudgeModal.showModal();
      }
    });
  });

  // Close modal handlers
  function closeModal() {
    if (nudgeModal) {
      if (typeof nudgeModal.close === "function") {
        nudgeModal.close();
      } else {
        nudgeModal.removeAttribute("open");
      }
    }
  }

  if (closeNudgeBtn) closeNudgeBtn.addEventListener("click", closeModal);
  if (cancelNudgeBtn) cancelNudgeBtn.addEventListener("click", closeModal);

  // Close when clicking modal backdrop
  if (nudgeModal) {
    nudgeModal.addEventListener("click", (e) => {
      const rect = nudgeModal.getBoundingClientRect();
      const inDialog = (
        rect.top <= e.clientY &&
        e.clientY <= rect.top + rect.height &&
        rect.left <= e.clientX &&
        e.clientX <= rect.left + rect.width
      );
      if (!inDialog) {
        closeModal();
      }
    });
  }

  // Handle Nudge Form AJAX Submission
  if (nudgeForm) {
    nudgeForm.addEventListener("submit", async function(e) {
      e.preventDefault();
      const formData = new FormData(nudgeForm);
      const submitBtn = nudgeForm.querySelector(".modal-btn-submit");

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Sending...";
      }

      try {
        const response = await fetch(nudgeForm.action, {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json"
          }
        });

        const data = await response.json();
        closeModal();

        if (data.success) {
          // Show toast notification
          showTemporaryToast(data.message || "Encouragement sent anonymously!");
        } else {
          alert(data.error || "Unable to send nudge. Please try again.");
        }
      } catch (err) {
        // Fallback to normal form submit on error
        nudgeForm.submit();
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = "Send Nudge &rarr;";
        }
      }
    });
  }

  function showTemporaryToast(message) {
    let toast = document.createElement("div");
    toast.className = "success-message";
    toast.style.position = "fixed";
    toast.style.bottom = "24px";
    toast.style.right = "24px";
    toast.style.zIndex = "9999";
    toast.style.boxShadow = "0 8px 24px rgba(0,0,0,0.15)";
    toast.style.borderRadius = "4px";
    toast.textContent = message;

    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.transition = "opacity 0.4s ease, transform 0.4s ease";
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      setTimeout(() => toast.remove(), 400);
    }, 4000);
  }
});
