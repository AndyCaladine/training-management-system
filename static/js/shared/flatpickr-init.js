/**
 * Shared Flatpickr initialiser.
 *
 * Why this exists:
 * Date inputs appear across several forms in the application. This helper
 * keeps the setup consistent while allowing each page to pass only the
 * selectors it actually uses.
 *
 * Expected config shape:
 * [
 *   { selector: "#start_date", clickOpens: true, allowInput: false },
 *   { selector: ".js-review-date", clickOpens: false, allowInput: false }
 * ]
 */
function initialiseFlatpickrFields(configs) {
    if (typeof flatpickr === "undefined") {
        return;
    }

    configs.forEach((config) => {
        const elements = document.querySelectorAll(config.selector);

        if (!elements.length) {
            return;
        }

        elements.forEach((element) => {
            flatpickr(element, {
                dateFormat: "Y-m-d",
                altInput: true,
                altFormat: "j F Y",
                allowInput: config.allowInput ?? false,
                clickOpens: config.clickOpens ?? true
            });
        });
    });
}