// Settings Feature JavaScript with Unsaved Changes Checker
document.addEventListener("DOMContentLoaded", function() {
  const darkModeToggle = document.getElementById("dark_mode");
  const emailToggle = document.getElementById("email_notifications");
  const nudgesToggle = document.getElementById("receive_nudges");
  const settingsForm = document.querySelector("form");
  const unsavedBanner = document.getElementById("unsaved-changes-banner");
  const discardBtn = document.getElementById("discard-changes-btn");

  // Record initial saved state from server
  const initialValues = {
    darkMode: darkModeToggle ? darkModeToggle.checked : false,
    email: emailToggle ? emailToggle.checked : false,
    nudges: nudgesToggle ? nudgesToggle.checked : false,
  };

  let isSubmitting = false;

  function isFormDirty() {
    const darkChanged = darkModeToggle && darkModeToggle.checked !== initialValues.darkMode;
    const emailChanged = emailToggle && emailToggle.checked !== initialValues.email;
    const nudgesChanged = nudgesToggle && nudgesToggle.checked !== initialValues.nudges;
    return darkChanged || emailChanged || nudgesChanged;
  }

  function updateDirtyUI() {
    const dirty = isFormDirty();

    if (unsavedBanner) {
      unsavedBanner.style.display = dirty ? "flex" : "none";
    }

    // Live preview theme only on this page
    if (darkModeToggle) {
      const activeDark = darkModeToggle.checked;
      document.body.classList.toggle("dark-theme", activeDark);
      document.documentElement.classList.toggle("dark-theme", activeDark);
    }
  }

  // Listen for changes
  [darkModeToggle, emailToggle, nudgesToggle].forEach(input => {
    if (input) {
      input.addEventListener("change", updateDirtyUI);
    }
  });

  // Discard / Reset button
  if (discardBtn) {
    discardBtn.addEventListener("click", function() {
      if (darkModeToggle) darkModeToggle.checked = initialValues.darkMode;
      if (emailToggle) emailToggle.checked = initialValues.email;
      if (nudgesToggle) nudgesToggle.checked = initialValues.nudges;
      updateDirtyUI();
    });
  }

  // Prevent leaving without saving if changes are pending
  if (settingsForm) {
    settingsForm.addEventListener("submit", function() {
      isSubmitting = true;
    });
  }

  // Browser navigation / reload / close tab warning
  window.addEventListener("beforeunload", function(e) {
    if (isFormDirty() && !isSubmitting) {
      // Revert preview so cached views or other windows remain accurate
      document.body.classList.toggle("dark-theme", initialValues.darkMode);
      document.documentElement.classList.toggle("dark-theme", initialValues.darkMode);
      e.preventDefault();
      e.returnValue = "You have unsaved changes in your settings. Are you sure you want to leave?";
      return e.returnValue;
    }
  });

  // In-page link clicks (e.g. clicking Home, Profile, Logout in the header)
  document.querySelectorAll("a[href]").forEach(link => {
    link.addEventListener("click", function(e) {
      if (isFormDirty() && !isSubmitting) {
        const confirmed = window.confirm("You have unsaved changes in your settings. If you leave now, your changes will not be saved. Do you want to leave?");
        if (!confirmed) {
          e.preventDefault();
        } else {
          // Revert temporary preview so destination screen loads with the saved server theme
          document.body.classList.toggle("dark-theme", initialValues.darkMode);
          document.documentElement.classList.toggle("dark-theme", initialValues.darkMode);
        }
      }
    });
  });
});
