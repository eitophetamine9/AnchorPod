// Home Feature JavaScript
document.addEventListener("DOMContentLoaded", function() {
  // 1. Daily checklist interactive toggle
  const goalRows = document.querySelectorAll(".goal-row");
  goalRows.forEach(row => {
    row.addEventListener("click", function(e) {
      const box = this.querySelector(".checkbox");
      if (box && !e.target.closest("form")) {
        box.classList.toggle("checked");
        box.textContent = box.classList.contains("checked") ? "✓" : "";
      }
    });
  });

  // 2. Anonymous Nudge Modal handling
  const nudgeModal = document.getElementById("nudge-modal");
  const openButtons = document.querySelectorAll(".open-nudge-modal-btn");
  const closeButton = document.getElementById("close-nudge-modal");
  const cancelButton = document.getElementById("cancel-nudge-btn");
  const recipientInput = document.getElementById("nudge-recipient-input");
  const targetNameEl = document.getElementById("nudge-target-name");

  if (nudgeModal) {
    openButtons.forEach(btn => {
      btn.addEventListener("click", function() {
        const recipientId = this.getAttribute("data-recipient-id");
        const recipientName = this.getAttribute("data-recipient-name");

        if (recipientInput) recipientInput.value = recipientId;
        if (targetNameEl) targetNameEl.textContent = recipientName;

        nudgeModal.showModal();
      });
    });

    const closeModal = () => nudgeModal.close();
    if (closeButton) closeButton.addEventListener("click", closeModal);
    if (cancelButton) cancelButton.addEventListener("click", closeModal);

    // Close when clicking on backdrop
    nudgeModal.addEventListener("click", function(e) {
      const rect = nudgeModal.getBoundingClientRect();
      const isInDialog = (
        rect.top <= e.clientY &&
        e.clientY <= rect.top + rect.height &&
        rect.left <= e.clientX &&
        e.clientX <= rect.left + rect.width
      );
      if (!isInDialog) {
        nudgeModal.close();
      }
    });
  }

  // 3. Smooth AJAX dismissal of received nudge banners
  const dismissForms = document.querySelectorAll(".nudge-dismiss-form");
  dismissForms.forEach(form => {
    form.addEventListener("submit", function(e) {
      e.preventDefault();
      const banner = this.closest(".nudge-alert-banner");
      const url = this.action;
      const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]')?.value;

      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
          "Accept": "application/json",
        },
      })
      .then(res => res.json())
      .then(data => {
        if (data.success && banner) {
          banner.style.transition = "opacity 0.25s ease, transform 0.25s ease";
          banner.style.opacity = "0";
          banner.style.transform = "translateY(-10px)";
          setTimeout(() => banner.remove(), 250);
        }
      })
      .catch(() => {
        // Fallback to normal submission on network failure
        form.submit();
      });
    });
  });
});
