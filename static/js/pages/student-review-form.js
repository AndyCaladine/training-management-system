document.addEventListener("DOMContentLoaded", () => {
    initialiseStudentReviewFormPage();
});

/**
 * Student periodic review form page controller.
 *
 * This file owns add/edit periodic review behaviour, including:
 * - date-picker setup for review period dates
 * - live character count and minimum-length validation for reflective fields
 *
 * The review form has enough page-specific behaviour to deserve its own file,
 * which keeps the main dashboard logic much cleaner.
 */
function initialiseStudentReviewFormPage() {
    initialiseReviewDateFields();
    initialisePeriodicReviewValidation();
}

/**
 * Initialises Flatpickr on periodic review date fields.
 */
function initialiseReviewDateFields() {
    initialiseFlatpickrFields([
        {
            selector: "#review_start_date",
            clickOpens: false,
            allowInput: false
        },
        {
            selector: "#review_end_date",
            clickOpens: false,
            allowInput: false
        }
    ]);
}

/**
 * Applies live character counting and minimum-length validation to all
 * reflective periodic review fields.
 *
 * Each field shares the same validation rule, so the page passes the field
 * configuration into the shared character count helper.
 */
function initialisePeriodicReviewValidation() {
    initialiseCharacterCountFields([
        {
            fieldId: "student_reflection",
            counterId: "student_reflection_counter",
            errorId: "student_reflection_live_error",
            minLength: 50
        },
        {
            fieldId: "achievements_last_period",
            counterId: "achievements_last_period_counter",
            errorId: "achievements_last_period_live_error",
            minLength: 50
        },
        {
            fieldId: "challenges_last_period",
            counterId: "challenges_last_period_counter",
            errorId: "challenges_last_period_live_error",
            minLength: 50
        },
        {
            fieldId: "goals_next_period",
            counterId: "goals_next_period_counter",
            errorId: "goals_next_period_live_error",
            minLength: 50
        },
        {
            fieldId: "support_needed",
            counterId: "support_needed_counter",
            errorId: "support_needed_live_error",
            minLength: 50
        }
    ]);
}