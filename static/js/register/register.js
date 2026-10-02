// Register Feature JavaScript
document.addEventListener("DOMContentLoaded", function() {
  const pwdInput = document.getElementById("id_password");
  const confirmInput = document.getElementById("id_password2");
  const form = document.querySelector("form");

  if (form && pwdInput && confirmInput) {
    form.addEventListener("submit", function(e) {
      if (pwdInput.value !== confirmInput.value) {
        e.preventDefault();
        alert("Passwords do not match. Please verify your password.");
        confirmInput.focus();
      }
    });
  }
});
