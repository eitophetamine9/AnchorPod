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
      const editBtn = e.target.closest(".goal-edit-btn");
      const row = e.target.closest(".goal-row");

      // Handle Edit Goal (Inline in-place editor)
      if (editBtn) {
        e.stopPropagation();
        const goalId = editBtn.getAttribute("data-goal-id");
        if (!goalId || !row) return;

        // If already editing, prevent duplicates
        if (row.querySelector(".goal-edit-container")) return;

        const titleSpan = row.querySelector(".goal-title");
        if (!titleSpan) return;

        const currentTitle = titleSpan.textContent.trim();

        // Temporarily hide display elements
        titleSpan.style.display = "none";
        editBtn.style.display = "none";
        const removeBtn = row.querySelector(".goal-remove-btn");
        if (removeBtn) removeBtn.style.display = "none";

        // Create inline editor container
        const editContainer = document.createElement("div");
        editContainer.className = "goal-edit-container";
        editContainer.innerHTML = `
          <input type="text" class="goal-edit-input" maxlength="120" value="${currentTitle.replace(/"/g, '&quot;')}" />
          <button type="button" class="goal-edit-save-btn" title="Save">&#10003;</button>
          <button type="button" class="goal-edit-cancel-btn" title="Cancel">&times;</button>
        `;

        // Prevent clicking inside edit container from toggling completion
        editContainer.addEventListener("click", function(ev) {
          ev.stopPropagation();
        });

        titleSpan.parentNode.insertBefore(editContainer, titleSpan.nextSibling);

        const editInput = editContainer.querySelector(".goal-edit-input");
        const saveBtn = editContainer.querySelector(".goal-edit-save-btn");
        const cancelBtn = editContainer.querySelector(".goal-edit-cancel-btn");

        editInput.focus();
        editInput.select();

        const closeEditor = () => {
          editContainer.remove();
          titleSpan.style.display = "";
          editBtn.style.display = "";
          if (removeBtn) removeBtn.style.display = "";
        };

        const saveEdit = () => {
          const newTitle = editInput.value.trim();
          if (!newTitle) {
            editInput.focus();
            return;
          }

          if (newTitle === currentTitle) {
            closeEditor();
            return;
          }

          // Optimistically update title span immediately (0ms visual response)
          titleSpan.textContent = newTitle;
          editBtn.setAttribute("data-title", newTitle);
          closeEditor();

          const csrfToken = getCsrfToken();
          const formData = new FormData();
          formData.append("title", newTitle);

          fetch(`/goals/edit/${goalId}/`, {
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
            if (!data.success) {
              // Revert if error
              titleSpan.textContent = currentTitle;
              editBtn.setAttribute("data-title", currentTitle);
              alert(data.error || "Failed to update habit.");
            }
          })
          .catch(err => {
            titleSpan.textContent = currentTitle;
            editBtn.setAttribute("data-title", currentTitle);
            console.error("Error editing goal:", err);
          });
        };

        saveBtn.addEventListener("click", function(ev) {
          ev.stopPropagation();
          saveEdit();
        });

        cancelBtn.addEventListener("click", function(ev) {
          ev.stopPropagation();
          closeEditor();
        });

        editInput.addEventListener("keydown", function(ev) {
          if (ev.key === "Enter") {
            ev.preventDefault();
            ev.stopPropagation();
            saveEdit();
          } else if (ev.key === "Escape") {
            ev.preventDefault();
            ev.stopPropagation();
            closeEditor();
          }
        });

        return;
      }

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

      // Handle Toggle Goal Completion (Optimistic UI for Instant Feedback)
      if (row && !e.target.closest("button") && !e.target.closest("form")) {
        const goalId = row.getAttribute("data-goal-id");
        if (!goalId) return;

        const csrfToken = getCsrfToken();
        const box = row.querySelector(".checkbox");

        // 1. Snapshot previous state for rollback on error
        const wasDone = row.classList.contains("goal-done");
        const willBeDone = !wasDone;

        // 2. Instant visual feedback (0ms optimistic toggle)
        row.classList.toggle("goal-done", willBeDone);
        if (box) {
          box.classList.toggle("checked", willBeDone);
          box.textContent = willBeDone ? "✓" : "";
        }

        // Optimistically update progress chip
        if (goalProgressChip) {
          const totalRows = goalList.querySelectorAll(".goal-row").length;
          const doneRows = goalList.querySelectorAll(".goal-row.goal-done").length;
          goalProgressChip.textContent = `${doneRows}/${totalRows} completed`;
        }

        // 3. Persist to Supabase in the background
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
            // Reconcile with authoritative server counts
            if (goalProgressChip && typeof data.completed_count === "number" && typeof data.total_count === "number") {
              goalProgressChip.textContent = `${data.completed_count}/${data.total_count} completed`;
            }
          } else {
            // Revert state if server returned an error
            row.classList.toggle("goal-done", wasDone);
            if (box) {
              box.classList.toggle("checked", wasDone);
              box.textContent = wasDone ? "✓" : "";
            }
            if (goalProgressChip) {
              const totalRows = goalList.querySelectorAll(".goal-row").length;
              const doneRows = goalList.querySelectorAll(".goal-row.goal-done").length;
              goalProgressChip.textContent = `${doneRows}/${totalRows} completed`;
            }
            console.error("Failed to toggle habit:", data.error);
          }
        })
        .catch(err => {
          // Revert state if network failure
          row.classList.toggle("goal-done", wasDone);
          if (box) {
            box.classList.toggle("checked", wasDone);
            box.textContent = wasDone ? "✓" : "";
          }
          if (goalProgressChip) {
            const totalRows = goalList.querySelectorAll(".goal-row").length;
            const doneRows = goalList.querySelectorAll(".goal-row.goal-done").length;
            goalProgressChip.textContent = `${doneRows}/${totalRows} completed`;
          }
          console.error("Network error toggling habit:", err);
        });
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
          newRow.setAttribute("data-category", data.goal.category);
          newRow.innerHTML = `
            <span class="checkbox"></span>
            <span class="goal-title">${data.goal.title}</span>
            <span class="goal-category-dot category-${data.goal.category}" title="${data.goal.category}"></span>
            <button type="button" class="goal-edit-btn" data-goal-id="${data.goal.id}" data-title="${data.goal.title}" title="Edit habit" aria-label="Edit habit">&#9998;</button>
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

  // Category Filtering for Goals
  const categoryFilterBar = document.getElementById("category-filter-bar");
  if (categoryFilterBar && goalList) {
    categoryFilterBar.addEventListener("click", function(e) {
      const btn = e.target.closest(".category-pill");
      if (!btn) return;

      categoryFilterBar.querySelectorAll(".category-pill").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");

      const filter = btn.getAttribute("data-filter") || "all";
      const rows = goalList.querySelectorAll(".goal-row");
      rows.forEach(row => {
        const cat = row.getAttribute("data-category");
        if (filter === "all" || cat === filter) {
          row.style.display = "flex";
        } else {
          row.style.display = "none";
        }
      });
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

  // 4. Instant tactile feedback on Daily Check-In submission
  const checkinForm = document.querySelector('form[action*="check_in"]');
  if (checkinForm) {
    checkinForm.addEventListener("submit", function() {
      const btn = checkinForm.querySelector(".checkin-button");
      if (btn) {
        btn.innerHTML = 'Checked in for today &#10003; <span>&rarr;</span>';
        btn.style.background = "#416b5e";
        btn.style.opacity = "0.9";
        btn.style.pointerEvents = "none";
      }
    });
  }
});
