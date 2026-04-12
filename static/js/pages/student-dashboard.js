document.addEventListener("DOMContentLoaded", () => {
    initialiseStudentDashboardPage();
});

/**
 * Student dashboard page controller.
 *
 * This file owns the interactive behaviour for the main student dashboard,
 * including:
 * - timesheet table filters
 * - learning tracker filters
 * - exam history filters
 * - dashboard section switching
 * - export section "select all" behaviour when present
 *
 * Form-specific logic for add/edit pages should live in their own page files,
 * not here. The aim is to keep the dashboard file focused and easy to scan.
 */
function initialiseStudentDashboardPage() {
    initialiseTimesheetFilters();
    initialiseLearningFilters();
    initialiseExamFilters();
    initialiseDashboardSectionToggle();
    initialiseExportSectionSelection();
}

/**
 * Timesheet table filters.
 *
 * Rows are filtered using the data-status and data-reviewer attributes
 * rendered into the table by the template.
 */
function initialiseTimesheetFilters() {
    createTableFilter({
        rowSelector: 'tbody tr[data-status]',
        filters: [
            { inputId: "statusFilter", dataKey: "status", match: "exact" },
            { inputId: "reviewerFilter", dataKey: "reviewer", match: "includes" }
        ],
        clearButtonId: "clearFilters"
    });
}

/**
 * Learning tracker filters.
 *
 * This keeps the learning section searchable without adding separate logic
 * for each filter input.
 */
function initialiseLearningFilters() {
    createTableFilter({
        rowSelector: 'tbody tr[data-learning-title]',
        filters: [
            { inputId: "learningTitleFilter", dataKey: "learningTitle", match: "includes" },
            { inputId: "learningCategoryFilter", dataKey: "learningCategory", match: "exact" },
            { inputId: "learningStatusFilter", dataKey: "learningStatus", match: "exact" },
            { inputId: "learningReviewStatusFilter", dataKey: "learningReviewStatus", match: "exact" }
        ],
        clearButtonId: "clearLearningFilters"
    });
}

/**
 * Exam history filters.
 *
 * Uses exact matching for level/result and partial matching for text-based
 * fields such as module, date, and score.
 */
function initialiseExamFilters() {
    createTableFilter({
        rowSelector: 'tbody tr[data-exam-level]',
        filters: [
            { inputId: "examLevelFilter", dataKey: "examLevel", match: "exact" },
            { inputId: "examModuleFilter", dataKey: "examModule", match: "includes" },
            { inputId: "examDateFilter", dataKey: "examDate", match: "includes" },
            { inputId: "examResultFilter", dataKey: "examResult", match: "exact" },
            { inputId: "examScoreFilter", dataKey: "examScore", match: "includes" }
        ],
        clearButtonId: "clearExamFilters"
    });
}

/**
 * Dashboard section switcher.
 *
 * The student dashboard presents multiple areas on one page. This behaviour
 * allows the user to focus on one section at a time or switch back to
 * viewing all sections together.
 */
function initialiseDashboardSectionToggle() {
    const cards = document.querySelectorAll(".dashboard-selector-card");
    const viewAllButton = document.querySelector(".dashboard-view-all-btn");

    const sections = {
        timesheets: document.getElementById("timesheets-section"),
        learning: document.getElementById("learning-section"),
        exams: document.getElementById("exams-section"),
        reviews: document.getElementById("reviews-section")
    };

    if (!cards.length) {
        return;
    }

    /**
     * Clears the active styling from all selector controls.
     */
    function clearActiveState() {
        cards.forEach((card) => {
            card.classList.remove("active");
        });

        if (viewAllButton) {
            viewAllButton.classList.remove("active");
        }
    }

    /**
     * Hides every dashboard section.
     */
    function hideAllSections() {
        Object.values(sections).forEach((section) => {
            if (section) {
                section.classList.add("dashboard-section-hidden");
            }
        });

        clearActiveState();
    }

    /**
     * Shows every dashboard section and marks the "View All" button active.
     */
    function showAllSections() {
        Object.values(sections).forEach((section) => {
            if (section) {
                section.classList.remove("dashboard-section-hidden");
            }
        });

        clearActiveState();

        if (viewAllButton) {
            viewAllButton.classList.add("active");
        }
    }

    /**
     * Shows one dashboard section and hides the rest.
     */
    function showOnlySection(target) {
        Object.entries(sections).forEach(([key, section]) => {
            if (!section) {
                return;
            }

            section.classList.toggle("dashboard-section-hidden", key !== target);
        });

        clearActiveState();

        const activeCard = document.querySelector(
            `.dashboard-selector-card[data-target="${target}"]`
        );

        if (activeCard) {
            activeCard.classList.add("active");
        }
    }

    cards.forEach((card) => {
        card.addEventListener("click", () => {
            showOnlySection(card.dataset.target);
        });
    });

    if (viewAllButton) {
        viewAllButton.addEventListener("click", showAllSections);
    }

    hideAllSections();
}

/**
 * Export page helper.
 *
 * This is safe to include here during the refactor because it only activates
 * when the expected export controls exist on the page.
 *
 * If the export area grows later, it can move into its own page file.
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

