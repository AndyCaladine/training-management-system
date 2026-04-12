/**
 * Shared live character count and minimum-length validation.
 *
 * Why this exists:
 * Multiple forms in the app use the same behaviour:
 * - display a live character count
 * - flag content that is present but too short
 * - preserve server-side validation styling until the user edits the field
 *
 * This helper keeps that behaviour consistent across learning records,
 * periodic reviews, and future reflective text fields.
 */
function initialiseCharacterCountFields(fieldConfigs) {
    fieldConfigs.forEach((config) => {
        const field = document.getElementById(config.fieldId);
        const counter = document.getElementById(config.counterId);
        const liveError = document.getElementById(config.errorId);
        const minLength = config.minLength ?? 0;

        if (!field || !counter || !liveError) {
            return;
        }

        /**
         * If the field is already marked invalid by the server,
         * keep that styling until the user starts editing.
         */
        if (field.classList.contains("input-error")) {
            field.dataset.serverError = "true";
        }

        /**
         * Refreshes the live counter and validation state for one field.
         */
        function updateFeedback() {
            const length = field.value.trim().length;
            const isTooShort = length > 0 && length < minLength;
            const hasServerError = Boolean(field.dataset.serverError);

            counter.textContent = `${length} characters`;
            counter.classList.toggle("too-short", isTooShort);
            liveError.style.display = isTooShort ? "block" : "none";

            if (isTooShort || hasServerError) {
                field.classList.add("input-error");
            } else {
                field.classList.remove("input-error");
            }
        }

        /**
         * Once the user edits the field, the live client-side validation
         * takes over from any previous server-side validation state.
         */
        field.addEventListener("input", () => {
            delete field.dataset.serverError;
            updateFeedback();
        });

        updateFeedback();
    });
}