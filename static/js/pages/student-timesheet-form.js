document.addEventListener("DOMContentLoaded", () => {
    initialiseStudentTimesheetFormPage();
});

/**
 * Student timesheet form page controller.
 *
 * This file owns add/edit timesheet form behaviour, including date-picker
 * setup for the start and end date fields.
 *
 * Keeping this separate from the dashboard file avoids mixing list-page
 * behaviour with form-page behaviour.
 */
function initialiseStudentTimesheetFormPage() {
    initialiseTimesheetDateFields();
}

/**
 * Initialises Flatpickr on timesheet date fields when they are present.
 *
 * The selectors are intentionally class-based so the same script can support
 * both add and edit templates without needing separate logic.
 */
function initialiseTimesheetDateFields() {
    initialiseFlatpickrFields([
        {
            selector: ".js-timesheet-start-date",
            clickOpens: false,
            allowInput: false
        },
        {
            selector: ".js-timesheet-end-date",
            clickOpens: true,
            allowInput: false
        }
    ]);
}