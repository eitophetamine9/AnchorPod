// Home Feature JavaScript
document.addEventListener("DOMContentLoaded", function() {
  const getCsrfToken = () => {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || "";
  };

  // 1. Interactive Self-Care Goal Toggles & Management
  const goalList = document.getElementById("goal-list");
  const goalProgressChip = document.getElementById("goal-progress-chip");
  const addGoalForm = document.getElementById("add-goal-form");

  if (goalList) {
    // Event delegation for toggling goal completion and deletion
    goalList.addEventListener("click", function(e) {
      const deleteBtn = e.target.closest(".goal-remove-btn");
      const row = e.target.closest(".goal-row");

      // Handle Delete Goal
      if (deleteBtn) {
        e.stopPropagation();
        const goalId = deleteBtn.getAttribute("data-goal-id");
        if (!goalId) return;

        const csrfToken = getCsrfToken();
        fetch(`/goals/delete/${goalId}/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
          },
        })
        .then(res => res.json())
        .then(data => {
          if (data.success && row) {
            row.style.transition = "opacity 0.2s ease, transform 0.2s ease";
            row.style.opacity = "0";
            row.style.transform = "translateX(-10px)";
            setTimeout(() => {
              row.remove();
              // Update counts
              const remainingRows = goalList.querySelectorAll(".goal-row");
              const remainingChecked = goalList.querySelectorAll(".goal-row.goal-done");
              if (goalProgressChip) {
                goalProgressChip.textContent = `${remainingChecked.length}/${remainingRows.length} completed`;
              }
            }, 200);
          }
        })
        .catch(err => console.error("Error deleting goal:", err));
        return;
      }

      // Handle Toggle Goal Completion
      if (row && !e.target.closest("button") && !e.target.closest("form")) {
        const goalId = row.getAttribute("data-goal-id");
        if (!goalId) return;

        const csrfToken = getCsrfToken();
        const box = row.querySelector(".checkbox");

        fetch(`/goals/toggle/${goalId}/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
          },
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            if (data.completed) {
              row.classList.add("goal-done");
              if (box) {
                box.classList.add("checked");
                box.textContent = "✓";
              }
            } else {
              row.classList.remove("goal-done");
              if (box) {
                box.classList.remove("checked");
                box.textContent = "";
              }
            }

            if (goalProgressChip) {
              goalProgressChip.textContent = `${data.completed_count}/${data.total_count} completed`;
            }
          }
        })
        .catch(err => console.error("Error toggling goal:", err));
      }
    });
  }

  // Handle Adding New Custom Goal
  if (addGoalForm) {
    addGoalForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const input = document.getElementById("add-goal-input");
      const categorySelect = document.getElementById("add-goal-category");
      const title = input?.value?.trim();
      const category = categorySelect?.value || "wellness";

      if (!title) return;

      const csrfToken = getCsrfToken();
      const formData = new FormData();
      formData.append("title", title);
      formData.append("category", category);

      fetch(addGoalForm.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
          "Accept": "application/json",
        },
        body: formData,
      })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.goal) {
          const emptyHint = goalList.querySelector(".empty-goals-hint");
          if (emptyHint) emptyHint.remove();

          // Create new goal row element
          const newRow = document.createElement("div");
          newRow.className = "goal-row";
          newRow.setAttribute("data-goal-id", data.goal.id);
          newRow.innerHTML = `
            <span class="checkbox"></span>
            <span class="goal-title">${data.goal.title}</span>
            <span class="goal-category-dot category-${data.goal.category}" title="${data.goal.category}"></span>
            <button type="button" class="goal-remove-btn" data-goal-id="${data.goal.id}" title="Remove habit" aria-label="Remove habit">&times;</button>
          `;

          goalList.appendChild(newRow);
          input.value = "";

          // Update counts
          const totalRows = goalList.querySelectorAll(".goal-row").length;
          const completedRows = goalList.querySelectorAll(".goal-row.goal-done").length;
          if (goalProgressChip) {
            goalProgressChip.textContent = `${completedRows}/${totalRows} completed`;
          }
        }
      })
      .catch(err => console.error("Error adding goal:", err));
    });
  }

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
        form.submit();
      });
    });
  });
});
