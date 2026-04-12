document.addEventListener("DOMContentLoaded", () => {
    initialiseStudentExportOptionsPage();
});

/**
 * Student export options page controller.
 *
 * This file owns the section selection behaviour for the PDF export page.
 * It keeps the export page independent from the student dashboard script.
 */
function initialiseStudentExportOptionsPage() {
    initialiseExportSectionSelection();
}

/**
 * Supports a single "select all" checkbox for export section choices.
 */
function initialiseExportSectionSelection() {
    const selectAllSections = document.getElementById("select_all_sections");
    const sectionCheckboxes = document.querySelectorAll('input[name="sections"]');

    if (!selectAllSections || !sectionCheckboxes.length) {
        return;
    }

    selectAllSections.addEventListener("change", () => {
        sectionCheckboxes.forEach((checkbox) => {
            checkbox.checked = selectAllSections.checked;
        });
    });

    sectionCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            const allChecked = [...sectionCheckboxes].every((item) => item.checked);
            selectAllSections.checked = allChecked;
        });
    });
}