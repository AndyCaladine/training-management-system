/*
===========================================================
Change Password Page Script
-----------------------------------------------------------
Handles:
- Password match validation
- Optional UX improvements
===========================================================
*/

document.addEventListener("DOMContentLoaded", () => {
    const newPassword = document.getElementById("new_password");
    const confirmPassword = document.getElementById("confirm_password");

    if (!newPassword || !confirmPassword) return;

    // ===========================================================
    // Create message element
    // ===========================================================
    const message = document.createElement("small");
    message.style.display = "block";
    message.style.marginTop = "0.25rem";

    confirmPassword.parentNode.appendChild(message);

    // ===========================================================
    // Password match check
    // ===========================================================
    function validatePasswords() {
        if (!confirmPassword.value) {
            message.textContent = "";
            return;
        }

        if (newPassword.value === confirmPassword.value) {
            message.textContent = "Passwords match ✔";
            message.style.color = "green";
        } else {
            message.textContent = "Passwords do not match";
            message.style.color = "red";
        }
    }

    newPassword.addEventListener("input", validatePasswords);
    confirmPassword.addEventListener("input", validatePasswords);
});