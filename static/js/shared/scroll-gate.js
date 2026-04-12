/**
 * Shared scroll-to-enable helper.
 *
 * Why this exists:
 * Registration and declaration-based forms use scrollable content areas
 * where the user must reach the bottom before the related checkbox becomes
 * available. This keeps the behaviour consistent and avoids repeating the
 * same event binding code.
 */
function initialiseScrollGate({
    scrollBox,
    checkbox,
    statusElement,
    completeText = "Read"
}) {
    if (!scrollBox || !checkbox || !statusElement) {
        return;
    }

    /**
     * Enables the checkbox once the user has reached the bottom of the box.
     * A small threshold is used so minor pixel rounding does not block access.
     */
    function handleScroll() {
        const reachedBottom =
            scrollBox.scrollTop + scrollBox.clientHeight >= scrollBox.scrollHeight - 5;

        if (!reachedBottom) {
            return;
        }

        checkbox.disabled = false;
        statusElement.textContent = completeText;

        if (checkbox.parentElement) {
            checkbox.parentElement.classList.remove("disabled-check");
        }
    }

    scrollBox.addEventListener("scroll", handleScroll);
}