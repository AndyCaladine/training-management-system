document.addEventListener("DOMContentLoaded", () => {
    initialiseStudentLearningFormPage();
});

/**
 * Student learning form page controller.
 *
 * This file owns add/edit learning record behaviour, including:
 * - date-picker setup for learning-related date fields
 * - live character count and minimum-length validation for learning outcomes
 *
 * Shared helpers keep repeated logic out of this file, while the page file
 * remains responsible for deciding which behaviours the form needs.
 */
function initialiseStudentLearningFormPage() {
    initialiseLearningDateFields();
    initialiseLearningOutcomesValidation();
}

/**
 * Initialises Flatpickr on learning form date fields.
 *
 * These selectors are shared by both add and edit templates so one page file
 * can safely support both journeys.
 */
function initialiseLearningDateFields() {
    initialiseFlatpickrFields([
        {
            selector: "#date_started",
            clickOpens: true,
            allowInput: false
        },
        {
            selector: "#date_completed",
            clickOpens: true,
            allowInput: false
        },
        {
            selector: "#certification_expiry_date",
            clickOpens: true,
            allowInput: false
        }
    ]);
}

/**
 * Applies live character counting and minimum-length validation to the
 * learning outcomes field.
 *
 * This mirrors the existing UX while moving the implementation into a
 * reusable shared helper.
 */
function initialiseLearningOutcomesValidation() {
    initialiseCharacterCountFields([
        {
            fieldId: "learning_outcomes",
            counterId: "learning_outcomes_counter",
            errorId: "learning_outcomes_live_error",
            minLength: 50
        }
    ]);
}