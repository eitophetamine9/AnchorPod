// Home Feature JavaScript
document.addEventListener("DOMContentLoaded", function() {
  // Handle interactive checkboxes in daily checklist
  const goalRows = document.querySelectorAll(".goal-row");
  goalRows.forEach(row => {
    row.addEventListener("click", function(e) {
      // Toggle visual checkbox
      const box = this.querySelector(".checkbox");
      if (box && !e.target.closest("form")) {
        box.classList.toggle("checked");
        box.textContent = box.classList.contains("checked") ? "✓" : "";
      }
    });
  });
});
