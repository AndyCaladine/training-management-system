/**
 * Shared table filtering helper.
 *
 * Why this exists:
 * Several dashboard areas use the same filtering pattern:
 * - read one or more filter input values
 * - compare them against data attributes on each row
 * - show only matching rows
 * - enable or disable the clear button
 *
 * Centralising this behaviour keeps the filtering consistent and avoids
 * maintaining near-identical logic in multiple page files.
 */
function createTableFilter({
    rowSelector,
    filters,
    clearButtonId,
    disabledClass = "button-disabled"
}) {
    const rows = document.querySelectorAll(rowSelector);
    const clearButton = clearButtonId ? document.getElementById(clearButtonId) : null;

    if (!rows.length || !filters.length) {
        return;
    }

    const filterConfigs = filters
        .map((config) => ({
            ...config,
            element: document.getElementById(config.inputId)
        }))
        .filter((config) => config.element);

    if (!filterConfigs.length) {
        return;
    }

    /**
     * Normalises values for reliable case-insensitive comparison.
     */
    function normalise(value) {
        return (value || "").toLowerCase().trim();
    }

    /**
     * Checks whether any filter currently has a value.
     * Used to control the clear button state.
     */
    function hasActiveFilters() {
        return filterConfigs.some(({ element }) => normalise(element.value) !== "");
    }

    /**
     * Updates the clear button so users can see whether filters are active.
     */
    function updateClearButton() {
        if (!clearButton) {
            return;
        }

        const active = hasActiveFilters();
        clearButton.disabled = !active;
        clearButton.classList.toggle(disabledClass, !active);
    }

    /**
     * Tests a single row against one filter rule.
     *
     * Match types:
     * - "exact" for select fields or strict values
     * - "includes" for partial text matching
     */
    function matchesFilter(row, config) {
        const filterValue = normalise(config.element.value);
        const rowValue = normalise(row.dataset[config.dataKey]);

        if (!filterValue) {
            return true;
        }

        if (config.match === "exact") {
            return rowValue === filterValue;
        }

        return rowValue.includes(filterValue);
    }

    /**
     * Applies all configured filters to all matching rows.
     */
    function applyFilters() {
        rows.forEach((row) => {
            const isMatch = filterConfigs.every((config) => matchesFilter(row, config));
            row.style.display = isMatch ? "" : "none";
        });

        updateClearButton();
    }

    /**
     * Binds each filter input to the right event type.
     * Select fields use change, text inputs use input.
     */
    filterConfigs.forEach(({ element }) => {
        const eventName = element.tagName === "SELECT" ? "change" : "input";
        element.addEventListener(eventName, applyFilters);
    });

    /**
     * Clears all filters in one action and re-runs the table filtering.
     */
    if (clearButton) {
        clearButton.addEventListener("click", () => {
            filterConfigs.forEach(({ element }) => {
                element.value = "";
            });

            applyFilters();
        });
    }

    updateClearButton();
}