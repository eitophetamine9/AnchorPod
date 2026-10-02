// Login Feature JavaScript
document.addEventListener("DOMContentLoaded", function() {
  const loginForm = document.querySelector("form");
  const usernameInput = document.getElementById("id_username");

  if (usernameInput && !usernameInput.value) {
    usernameInput.focus();
  }

  if (loginForm) {
    loginForm.addEventListener("submit", function() {
      const submitBtn = loginForm.querySelector("button[type='submit']");
      if (submitBtn) {
        submitBtn.style.opacity = "0.7";
        submitBtn.style.pointerEvents = "none";
      }
    });
  }
});
