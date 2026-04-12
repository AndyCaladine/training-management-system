/**
 * Main site-wide JavaScript.
 *
 * Purpose:
 * This file is reserved for behaviour that is genuinely global across the app.
 * It should stay small and predictable. Page-specific logic belongs in the
 * relevant file under static/js/pages/.
 */

document.addEventListener("DOMContentLoaded", () => {
    initialiseDismissibleMessages();
});

/**
 * Allows users to dismiss flash messages or other temporary alerts.
 *
 * Expected markup:
 * - A container with the class .flash-message
 * - A button inside with the class .flash-dismiss
 */
function initialiseDismissibleMessages() {
    const dismissButtons = document.querySelectorAll(".flash-dismiss");

    if (!dismissButtons.length) {
        return;
    }

    dismissButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const message = button.closest(".flash-message");

            if (message) {
                message.remove();
            }
        });
    });
}