// Initialise Flatpickr only for fields that are meant to use it
document.addEventListener("DOMContentLoaded", () => {
    const flatpickrConfigs = [
        { selector: ".js-timesheet-start-date", clickOpens: false, allowInput: false },
        { selector: ".js-timesheet-end-date", clickOpens: true, allowInput: false },
        { selector: "#date_started", clickOpens: true, allowInput: false },
        { selector: "#date_completed", clickOpens: true, allowInput: false },
        { selector: "#certification_expiry_date", clickOpens: true, allowInput: false },
        { selector: "#review_start_date", clickOpens: false, allowInput: false },
        { selector: "#review_end_date", clickOpens: false, allowInput: false }
    ];

    flatpickrConfigs.forEach((field) => {
        const elements = document.querySelectorAll(field.selector);

        if (!elements.length) return;

        elements.forEach((element) => {
            flatpickr(element, {
                dateFormat: "Y-m-d",
                altInput: true,
                altFormat: "j F Y",
                allowInput: field.allowInput,
                clickOpens: field.clickOpens
            });
        });
    });

//Filter function for Timesheets=
    const statusFilter = document.getElementById("statusFilter");
    const reviewerFilter = document.getElementById("reviewerFilter");
    const clearFilters = document.getElementById("clearFilters");
    const tableRows = document.querySelectorAll("tbody tr[data-status]");

    function filtersActive() {
        return (
            (statusFilter && statusFilter.value !== "") ||
            (reviewerFilter && reviewerFilter.value.trim() !== "")
        );
    }

    function updateClearButton() {
        if (!clearFilters) return;

        if (filtersActive()) {
            clearFilters.disabled = false;
            clearFilters.classList.remove("button-disabled");
        } else {
            clearFilters.disabled = true;
            clearFilters.classList.add("button-disabled");
        }
    }

    function applyFilters() {
        const statusValue = statusFilter ? statusFilter.value.toLowerCase() : "";
        const reviewerValue = reviewerFilter ? reviewerFilter.value.toLowerCase().trim() : "";

        tableRows.forEach((row) => {
            const rowStatus = (row.dataset.status || "").toLowerCase();
            const rowReviewer = (row.dataset.reviewer || "").toLowerCase();

            const matchesStatus = !statusValue || rowStatus === statusValue;
            const matchesReviewer = !reviewerValue || rowReviewer.includes(reviewerValue);

            row.style.display = matchesStatus && matchesReviewer ? "" : "none";
        });

        updateClearButton();
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", applyFilters);
    }

    if (reviewerFilter) {
        reviewerFilter.addEventListener("input", applyFilters);
    }

    if (clearFilters) {
        clearFilters.addEventListener("click", () => {
            if (statusFilter) statusFilter.value = "";
            if (reviewerFilter) reviewerFilter.value = "";
            applyFilters();
        });
    }

    updateClearButton();
});

//Filters for Student Dashboard (Timesheet)
const statusFilter = document.getElementById("statusFilter");
const reviewerFilter = document.getElementById("reviewerFilter");
const clearFilters = document.getElementById("clearFilters");
const tableRows = document.querySelectorAll("tbody tr[data-status]");

function filtersActive() {
    return (
        (statusFilter && statusFilter.value !== "") ||
        (reviewerFilter && reviewerFilter.value.trim() !== "")
    );
}

function updateClearButton() {
    if (!clearFilters) return;

    if (filtersActive()) {
        clearFilters.disabled = false;
        clearFilters.classList.remove("button-disabled");
    } else {
        clearFilters.disabled = true;
        clearFilters.classList.add("button-disabled");
    }
}

function applyFilters() {
    const statusValue = statusFilter ? statusFilter.value.toLowerCase() : "";
    const reviewerValue = reviewerFilter ? reviewerFilter.value.toLowerCase().trim() : "";

    tableRows.forEach((row) => {
        const rowStatus = (row.dataset.status || "").toLowerCase();
        const rowReviewer = (row.dataset.reviewer || "").toLowerCase();

        const matchesStatus = !statusValue || rowStatus === statusValue;
        const matchesReviewer = !reviewerValue || rowReviewer.includes(reviewerValue);

        row.style.display = matchesStatus && matchesReviewer ? "" : "none";
    });

    updateClearButton();
}

if (statusFilter) {
    statusFilter.addEventListener("change", applyFilters);
}

if (reviewerFilter) {
    reviewerFilter.addEventListener("input", applyFilters);
}

if (clearFilters) {
    clearFilters.addEventListener("click", () => {
        if (statusFilter) statusFilter.value = "";
        if (reviewerFilter) reviewerFilter.value = "";
        applyFilters();
    });
}

// Run once on load
updateClearButton();

// Add Learning function in SMART Obvjectives

    const learningOutcomesField = document.getElementById("learning_outcomes");
    const learningOutcomesCounter = document.getElementById("learning_outcomes_counter");
    const learningOutcomesLiveError = document.getElementById("learning_outcomes_live_error");

    function updateLearningOutcomesFeedback() {
        if (!learningOutcomesField || !learningOutcomesCounter || !learningOutcomesLiveError) return;

        const length = learningOutcomesField.value.trim().length;
        learningOutcomesCounter.textContent = `${length} characters`;

        if (length > 0 && length < 50) {
            learningOutcomesField.classList.add("input-error");
            learningOutcomesCounter.classList.add("too-short");
            learningOutcomesLiveError.style.display = "block";
        } else {
            learningOutcomesCounter.classList.remove("too-short");
            learningOutcomesLiveError.style.display = "none";

            // Only remove the live error styling if there isn't a server-side error on this field
            if (!learningOutcomesField.dataset.serverError) {
                learningOutcomesField.classList.remove("input-error");
            }
        }
    }

    if (learningOutcomesField) {
        if (learningOutcomesField.classList.contains("input-error")) {
            learningOutcomesField.dataset.serverError = "true";
        }

        learningOutcomesField.addEventListener("input", () => {
            delete learningOutcomesField.dataset.serverError;
            updateLearningOutcomesFeedback();
        });

        updateLearningOutcomesFeedback();
    }
//Filters for the Learning Tracker 

    const learningTitleFilter = document.getElementById("learningTitleFilter");
    const learningCategoryFilter = document.getElementById("learningCategoryFilter");
    const learningStatusFilter = document.getElementById("learningStatusFilter");
    const learningReviewStatusFilter = document.getElementById("learningReviewStatusFilter");
    const clearLearningFilters = document.getElementById("clearLearningFilters");
    const learningRows = document.querySelectorAll("tbody tr[data-learning-title]");

    function learningFiltersActive() {
        return (
            (learningTitleFilter && learningTitleFilter.value.trim() !== "") ||
            (learningCategoryFilter && learningCategoryFilter.value !== "") ||
            (learningStatusFilter && learningStatusFilter.value !== "") ||
            (learningReviewStatusFilter && learningReviewStatusFilter.value !== "")
        );
    }

    function updateLearningClearButton() {
        if (!clearLearningFilters) return;

        if (learningFiltersActive()) {
            clearLearningFilters.disabled = false;
            clearLearningFilters.classList.remove("button-disabled");
        } else {
            clearLearningFilters.disabled = true;
            clearLearningFilters.classList.add("button-disabled");
        }
    }

    function applyLearningFilters() {
        const titleValue = learningTitleFilter ? learningTitleFilter.value.toLowerCase().trim() : "";
        const categoryValue = learningCategoryFilter ? learningCategoryFilter.value.toLowerCase() : "";
        const statusValue = learningStatusFilter ? learningStatusFilter.value.toLowerCase() : "";
        const reviewStatusValue = learningReviewStatusFilter ? learningReviewStatusFilter.value.toLowerCase() : "";

        learningRows.forEach((row) => {
            const rowTitle = (row.dataset.learningTitle || "").toLowerCase();
            const rowCategory = (row.dataset.learningCategory || "").toLowerCase();
            const rowStatus = (row.dataset.learningStatus || "").toLowerCase();
            const rowReviewStatus = (row.dataset.learningReviewStatus || "").toLowerCase();

            const matchesTitle = !titleValue || rowTitle.includes(titleValue);
            const matchesCategory = !categoryValue || rowCategory === categoryValue;
            const matchesStatus = !statusValue || rowStatus === statusValue;
            const matchesReviewStatus = !reviewStatusValue || rowReviewStatus === reviewStatusValue;

            row.style.display =
                matchesTitle && matchesCategory && matchesStatus && matchesReviewStatus ? "" : "none";
        });

        updateLearningClearButton();
    }

    if (learningTitleFilter) {
        learningTitleFilter.addEventListener("input", applyLearningFilters);
    }

    if (learningCategoryFilter) {
        learningCategoryFilter.addEventListener("change", applyLearningFilters);
    }

    if (learningStatusFilter) {
        learningStatusFilter.addEventListener("change", applyLearningFilters);
    }

    if (learningReviewStatusFilter) {
        learningReviewStatusFilter.addEventListener("change", applyLearningFilters);
    }

    if (clearLearningFilters) {
        clearLearningFilters.addEventListener("click", () => {
            if (learningTitleFilter) learningTitleFilter.value = "";
            if (learningCategoryFilter) learningCategoryFilter.value = "";
            if (learningStatusFilter) learningStatusFilter.value = "";
            if (learningReviewStatusFilter) learningReviewStatusFilter.value = "";
            applyLearningFilters();
        });
    }

    updateLearningClearButton();

// Exam Filter history
        const examLevelFilter = document.getElementById("examLevelFilter");
    const examModuleFilter = document.getElementById("examModuleFilter");
    const examDateFilter = document.getElementById("examDateFilter");
    const examResultFilter = document.getElementById("examResultFilter");
    const examScoreFilter = document.getElementById("examScoreFilter");
    const clearExamFilters = document.getElementById("clearExamFilters");
    const examRows = document.querySelectorAll("tbody tr[data-exam-level]");

    function examFiltersActive() {
        return (
            (examLevelFilter && examLevelFilter.value !== "") ||
            (examModuleFilter && examModuleFilter.value.trim() !== "") ||
            (examDateFilter && examDateFilter.value.trim() !== "") ||
            (examResultFilter && examResultFilter.value !== "") ||
            (examScoreFilter && examScoreFilter.value.trim() !== "")
        );
    }

    function updateExamClearButton() {
        if (!clearExamFilters) return;

        if (examFiltersActive()) {
            clearExamFilters.disabled = false;
            clearExamFilters.classList.remove("button-disabled");
        } else {
            clearExamFilters.disabled = true;
            clearExamFilters.classList.add("button-disabled");
        }
    }

    function applyExamFilters() {
        const levelValue = examLevelFilter ? examLevelFilter.value.toLowerCase() : "";
        const moduleValue = examModuleFilter ? examModuleFilter.value.toLowerCase().trim() : "";
        const dateValue = examDateFilter ? examDateFilter.value.toLowerCase().trim() : "";
        const resultValue = examResultFilter ? examResultFilter.value.toLowerCase() : "";
        const scoreValue = examScoreFilter ? examScoreFilter.value.toLowerCase().trim() : "";

        examRows.forEach((row) => {
            const rowLevel = (row.dataset.examLevel || "").toLowerCase();
            const rowModule = (row.dataset.examModule || "").toLowerCase();
            const rowDate = (row.dataset.examDate || "").toLowerCase();
            const rowResult = (row.dataset.examResult || "").toLowerCase();
            const rowScore = (row.dataset.examScore || "").toLowerCase();

            const matchesLevel = !levelValue || rowLevel === levelValue;
            const matchesModule = !moduleValue || rowModule.includes(moduleValue);
            const matchesDate = !dateValue || rowDate.includes(dateValue);
            const matchesResult = !resultValue || rowResult === resultValue;
            const matchesScore = !scoreValue || rowScore.includes(scoreValue);

            row.style.display =
                matchesLevel && matchesModule && matchesDate && matchesResult && matchesScore
                    ? ""
                    : "none";
        });

        updateExamClearButton();
    }

    if (examLevelFilter) {
        examLevelFilter.addEventListener("change", applyExamFilters);
    }

    if (examModuleFilter) {
        examModuleFilter.addEventListener("input", applyExamFilters);
    }

    if (examDateFilter) {
        examDateFilter.addEventListener("input", applyExamFilters);
    }

    if (examResultFilter) {
        examResultFilter.addEventListener("change", applyExamFilters);
    }

    if (examScoreFilter) {
        examScoreFilter.addEventListener("input", applyExamFilters);
    }

    if (clearExamFilters) {
        clearExamFilters.addEventListener("click", () => {
            if (examLevelFilter) examLevelFilter.value = "";
            if (examModuleFilter) examModuleFilter.value = "";
            if (examDateFilter) examDateFilter.value = "";
            if (examResultFilter) examResultFilter.value = "";
            if (examScoreFilter) examScoreFilter.value = "";
            applyExamFilters();
        });
    }

    updateExamClearButton();

// Validation for the review fields to ensure more that 50 char

    const periodicReviewFields = [
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
    ];

    periodicReviewFields.forEach((config) => {
        const field = document.getElementById(config.fieldId);
        const counter = document.getElementById(config.counterId);
        const liveError = document.getElementById(config.errorId);

        if (!field || !counter || !liveError) return;

        function updateFieldFeedback() {
            const length = field.value.trim().length;
            counter.textContent = `${length} characters`;

            if (length > 0 && length < config.minLength) {
                field.classList.add("input-error");
                counter.classList.add("too-short");
                liveError.style.display = "block";
            } else {
                counter.classList.remove("too-short");
                liveError.style.display = "none";

                if (!field.dataset.serverError) {
                    field.classList.remove("input-error");
                }
            }
        }

        if (field.classList.contains("input-error")) {
            field.dataset.serverError = "true";
        }

        field.addEventListener("input", () => {
            delete field.dataset.serverError;
            updateFieldFeedback();
        });

        updateFieldFeedback();
    });

// Dashboard section toggle
document.addEventListener("DOMContentLoaded", () => {
    const dashboardCards = document.querySelectorAll(".dashboard-selector-card");
    const viewAllButton = document.querySelector(".dashboard-view-all-btn");

    const dashboardSections = {
        timesheets: document.getElementById("timesheets-section"),
        learning: document.getElementById("learning-section"),
        exams: document.getElementById("exams-section"),
        reviews: document.getElementById("reviews-section")
    };

    if (!dashboardCards.length) return;

    function clearDashboardActiveState() {
        dashboardCards.forEach((card) => card.classList.remove("active"));
        if (viewAllButton) {
            viewAllButton.classList.remove("active");
        }
    }

    function hideAllDashboardSections() {
        Object.values(dashboardSections).forEach((section) => {
            if (section) {
                section.classList.add("dashboard-section-hidden");
            }
        });

        clearDashboardActiveState();
    }

    function showAllDashboardSections() {
        Object.values(dashboardSections).forEach((section) => {
            if (section) {
                section.classList.remove("dashboard-section-hidden");
            }
        });

        clearDashboardActiveState();

        if (viewAllButton) {
            viewAllButton.classList.add("active");
        }
    }

    function showOnlyDashboardSection(target) {
        Object.entries(dashboardSections).forEach(([key, section]) => {
            if (!section) return;

            if (key === target) {
                section.classList.remove("dashboard-section-hidden");
            } else {
                section.classList.add("dashboard-section-hidden");
            }
        });

        clearDashboardActiveState();

        const activeCard = document.querySelector(`.dashboard-selector-card[data-target="${target}"]`);
        if (activeCard) {
            activeCard.classList.add("active");
        }
    }

    dashboardCards.forEach((card) => {
        card.addEventListener("click", () => {
            showOnlyDashboardSection(card.dataset.target);
        });
    });

    if (viewAllButton) {
        viewAllButton.addEventListener("click", () => {
            showAllDashboardSections();
        });
    }

    hideAllDashboardSections();
});

// Select all export sections
document.addEventListener("DOMContentLoaded", () => {
    const selectAllSections = document.getElementById("select_all_sections");
    const sectionCheckboxes = document.querySelectorAll('input[name="sections"]');

    if (!selectAllSections || !sectionCheckboxes.length) return;

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
});

// Student Registration logic and look and feel
document.addEventListener("DOMContentLoaded", function () {
    const accessCode = document.getElementById("access_code");
    const accessCodeMessage = document.getElementById("access-code-message");

    const firstName = document.getElementById("first_name");
    const lastName = document.getElementById("last_name");
    const employerName = document.getElementById("employer_name");
    const startDate = document.getElementById("start_date");
    const years = document.getElementById("years");
    const months = document.getElementById("months");
    const days = document.getElementById("days");

    const postcode = document.getElementById("postcode");
    const findAddressBtn = document.getElementById("find-address-btn");
    const addressSelect = document.getElementById("address_select");
    const addressLookupMessage = document.getElementById("address-lookup-message");

    const addressLine1 = document.getElementById("address_line_1");
    const addressLine2 = document.getElementById("address_line_2");
    const townCity = document.getElementById("town_city");
    const county = document.getElementById("county");

    const dobDay = document.getElementById("dob_day");
    const dobMonth = document.getElementById("dob_month");
    const dobYear = document.getElementById("dob_year");
    const dobHidden = document.getElementById("date_of_birth");
    const dobYearOptions = document.getElementById("dob-year-options");

    const manualAddressToggle = document.getElementById("manual-address-toggle");
    const manualAddressFields = document.getElementById("manual-address-fields");

    const summaryName = document.getElementById("summary-name");
    const summaryEmployer = document.getElementById("summary-employer");
    const summaryStart = document.getElementById("summary-start");
    const summaryDuration = document.getElementById("summary-duration");
    const summaryEnd = document.getElementById("summary-end");

    const agreementPreviewText = document.getElementById("agreement-preview-text");

    const termsStudentName = document.getElementById("terms-student-name");
    const termsEmployerName = document.getElementById("terms-employer-name");
    const termsStartDate = document.getElementById("terms-start-date");
    const termsDuration = document.getElementById("terms-duration");
    const termsEndDate = document.getElementById("terms-end-date");

    const termsScrollBox = document.getElementById("terms-scroll-box");
    const gdprScrollBox = document.getElementById("gdpr-scroll-box");

    const termsCheckbox = document.getElementById("terms_agreed");
    const gdprCheckbox = document.getElementById("gdpr_agreed");

    const termsStatus = document.getElementById("terms-status");
    const gdprStatus = document.getElementById("gdpr-status");

    const signatureName = document.getElementById("signature-name");
    const signatureDate = document.getElementById("signature-date");

    if (!firstName) return;

    function formatDate(dateString) {
        if (!dateString) return "—";
        const date = new Date(dateString + "T00:00:00");
        if (Number.isNaN(date.getTime())) return "—";

        return date.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "long",
            year: "numeric"
        });
    }

    function populateDobYears() {
        if (!dobYearOptions) return;

        const currentYear = new Date().getFullYear();
        dobYearOptions.innerHTML = "";

        for (let year = 1901; year <= currentYear; year++) {
            const option = document.createElement("option");
            option.value = String(year);
            dobYearOptions.appendChild(option);
        }
    }

    function getMonthNumber(monthName) {
        const monthsMap = {
            january: "01",
            february: "02",
            march: "03",
            april: "04",
            may: "05",
            june: "06",
            july: "07",
            august: "08",
            september: "09",
            october: "10",
            november: "11",
            december: "12"
        };

        return monthsMap[(monthName || "").trim().toLowerCase()] || "";
    }

    function updateHiddenDob() {
        if (!dobDay || !dobMonth || !dobYear || !dobHidden) return;

        const rawDay = (dobDay.value || "").trim();
        const rawYear = (dobYear.value || "").trim();
        const month = getMonthNumber(dobMonth.value);

        const dayNumber = parseInt(rawDay, 10);
        const yearNumber = parseInt(rawYear, 10);

        const validDay = !Number.isNaN(dayNumber) && dayNumber >= 1 && dayNumber <= 31;
        const validYear = !Number.isNaN(yearNumber) && rawYear.length === 4;

        if (validDay && month && validYear) {
            const day = String(dayNumber).padStart(2, "0");
            dobHidden.value = `${rawYear}-${month}-${day}`;
        } else {
            dobHidden.value = "";
        }
    }

    function buildDurationText() {
        const y = parseInt(years?.value || 0, 10);
        const m = parseInt(months?.value || 0, 10);
        const d = parseInt(days?.value || 0, 10);

        const parts = [];

        if (y > 0) parts.push(`${y} year${y !== 1 ? "s" : ""}`);
        if (m > 0) parts.push(`${m} month${m !== 1 ? "s" : ""}`);
        if (d > 0) parts.push(`${d} day${d !== 1 ? "s" : ""}`);

        return parts.length ? parts.join(", ") : "—";
    }

    function calculateEndDate() {
        if (!startDate || !startDate.value) return "—";

        const date = new Date(startDate.value + "T00:00:00");
        const y = parseInt(years?.value || 0, 10);
        const m = parseInt(months?.value || 0, 10);
        const d = parseInt(days?.value || 0, 10);

        if (Number.isNaN(date.getTime())) return "—";
        if (y === 0 && m === 0 && d === 0) return "—";

        date.setFullYear(date.getFullYear() + y);
        date.setMonth(date.getMonth() + m);
        date.setDate(date.getDate() + d);

        return date.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "long",
            year: "numeric"
        });
    }

    function updatePreview() {
        const fullName = `${firstName?.value || ""} ${lastName?.value || ""}`.trim() || "—";
        const employer = employerName?.value?.trim() || "—";
        const formattedStart = formatDate(startDate?.value || "");
        const durationText = buildDurationText();
        const endDateText = calculateEndDate();

        if (summaryName) summaryName.textContent = fullName;
        if (summaryEmployer) summaryEmployer.textContent = employer;
        if (summaryStart) summaryStart.textContent = formattedStart;
        if (summaryDuration) summaryDuration.textContent = durationText;
        if (summaryEnd) summaryEnd.textContent = endDateText;

        if (termsStudentName) {
            termsStudentName.textContent = fullName !== "—" ? fullName : "the student";
        }

        if (termsEmployerName) {
            termsEmployerName.textContent = employer !== "—" ? employer : "the employer";
        }

        if (termsStartDate) {
            termsStartDate.textContent = formattedStart !== "—" ? formattedStart : "the selected start date";
        }

        if (termsDuration) {
            termsDuration.textContent = durationText !== "—" ? durationText : "the selected duration";
        }

        if (termsEndDate) {
            termsEndDate.textContent = endDateText !== "—" ? endDateText : "the calculated end date";
        }

        if (agreementPreviewText) {
            agreementPreviewText.textContent =
                `This training agreement is between ${fullName !== "—" ? fullName : "the student"} and ` +
                `${employer !== "—" ? employer : "the employer"}. ` +
                `The agreement will begin on ${formattedStart !== "—" ? formattedStart : "the selected start date"} ` +
                `and will run for ${durationText !== "—" ? durationText : "the selected duration"}, ` +
                `ending on ${endDateText !== "—" ? endDateText : "the calculated end date"}. ` +
                `During this period, the student is expected to participate in the agreed programme, ` +
                `maintain training records, and submit required learning activity, timesheets, and periodic reviews ` +
                `in line with the expectations of the training arrangement.`;
        }
    }

    function enableOnScroll(scrollBox, checkbox, statusEl, completeText) {
        if (!scrollBox || !checkbox || !statusEl) return;

        scrollBox.addEventListener("scroll", function () {
            const reachedBottom =
                scrollBox.scrollTop + scrollBox.clientHeight >= scrollBox.scrollHeight - 5;

            if (reachedBottom) {
                checkbox.disabled = false;

                if (checkbox.parentElement) {
                    checkbox.parentElement.classList.remove("disabled-check");
                }

                statusEl.textContent = completeText;
            }
        });
    }

    function updateSignature() {
        const fullName = `${firstName?.value || ""} ${lastName?.value || ""}`.trim();

        if (termsCheckbox?.checked && gdprCheckbox?.checked && fullName) {
            const today = new Date().toLocaleDateString("en-GB", {
                day: "2-digit",
                month: "long",
                year: "numeric"
            });

            if (signatureName) signatureName.textContent = fullName;
            if (signatureDate) signatureDate.textContent = `Signed electronically on ${today}`;
        } else {
            if (signatureName) signatureName.textContent = "Awaiting agreement";
            if (signatureDate) {
                signatureDate.textContent = "Date will appear once declarations are accepted";
            }
        }
    }

    function toggleManualAddress() {
        if (!manualAddressFields) return;

        manualAddressFields.classList.toggle("show");

        if (manualAddressToggle) {
            manualAddressToggle.textContent = manualAddressFields.classList.contains("show")
                ? "Hide manual address entry"
                : "Enter address manually";
        }
    }

    function populateAddressFields(address) {
        if (!address) return;

        if (addressLine1) addressLine1.value = address.address_line_1 || "";
        if (addressLine2) addressLine2.value = address.address_line_2 || "";
        if (townCity) townCity.value = address.town_city || "";
        if (county) county.value = address.county || "";
        if (postcode) postcode.value = address.postcode || postcode.value || "";

        if (manualAddressFields && !manualAddressFields.classList.contains("show")) {
            manualAddressFields.classList.add("show");
        }

        if (manualAddressToggle) {
            manualAddressToggle.textContent = "Hide manual address entry";
        }
    }

    async function lookupAccessCode() {
        if (!accessCode || !employerName || !accessCodeMessage) return;

        const code = accessCode.value.trim();

        employerName.value = "";
        accessCodeMessage.textContent = "";
        accessCodeMessage.classList.remove("success", "error");

        if (!code) {
            updatePreview();
            return;
        }

        try {
            const response = await fetch("/register/student/access-code-lookup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ access_code: code })
            });

            const result = await response.json();

            if (response.ok && result.valid) {
                employerName.value = result.employer_name || "";
                accessCodeMessage.textContent = result.message || "Access code accepted.";
                accessCodeMessage.classList.add("success");
            } else {
                employerName.value = "";
                accessCodeMessage.textContent = result.message || "Access code not recognised.";
                accessCodeMessage.classList.add("error");
            }
        } catch (error) {
            employerName.value = "";
            accessCodeMessage.textContent = "Unable to validate access code right now.";
            accessCodeMessage.classList.add("error");
        }

        updatePreview();
    }

    async function lookupDemoAddresses() {
        if (!postcode || !addressSelect || !addressLookupMessage) return;

        const postcodeValue = postcode.value.trim();

        addressLookupMessage.textContent = "";
        addressLookupMessage.classList.remove("success", "error");
        addressSelect.innerHTML = '<option value="">Select an address</option>';

        if (!postcodeValue) {
            addressLookupMessage.textContent = "Please enter a postcode.";
            addressLookupMessage.classList.add("error");
            return;
        }

        try {
            const response = await fetch("/register/student/address-lookup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ postcode: postcodeValue })
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                addressLookupMessage.textContent =
                    result.message || "No demo addresses found for that postcode.";
                addressLookupMessage.classList.add("error");
                return;
            }

            result.addresses.forEach((address, index) => {
                const option = document.createElement("option");
                option.value = String(index);
                option.textContent = address.label;
                option.dataset.address = JSON.stringify(address);
                addressSelect.appendChild(option);
            });

            addressLookupMessage.textContent =
                result.message || `${result.addresses.length} address(es) found.`;
            addressLookupMessage.classList.add("success");
        } catch (error) {
            addressLookupMessage.textContent = "Unable to look up demo addresses right now.";
            addressLookupMessage.classList.add("error");
        }
    }

    if (manualAddressToggle) {
        manualAddressToggle.addEventListener("click", toggleManualAddress);
    }

    if (findAddressBtn) {
        findAddressBtn.addEventListener("click", lookupDemoAddresses);
    }

    if (addressSelect) {
        addressSelect.addEventListener("change", function () {
            const selectedOption = addressSelect.options[addressSelect.selectedIndex];
            if (!selectedOption || !selectedOption.dataset.address) return;

            try {
                const address = JSON.parse(selectedOption.dataset.address);
                populateAddressFields(address);
            } catch (error) {
                // no-op
            }
        });
    }

    if (accessCode) {
        let accessCodeTimer;

        accessCode.addEventListener("input", function () {
            clearTimeout(accessCodeTimer);

            accessCodeTimer = setTimeout(() => {
                lookupAccessCode();
            }, 400);
        });

        accessCode.addEventListener("blur", lookupAccessCode);
    }

    [firstName, lastName, employerName, startDate, years, months, days].forEach((field) => {
        if (!field) return;

        field.addEventListener("input", function () {
            updatePreview();
            updateSignature();
        });

        field.addEventListener("change", function () {
            updatePreview();
            updateSignature();
        });
    });

    [dobDay, dobMonth, dobYear].forEach((field) => {
        if (!field) return;

        field.addEventListener("input", updateHiddenDob);
        field.addEventListener("change", updateHiddenDob);
    });

    [termsCheckbox, gdprCheckbox].forEach((field) => {
        if (!field) return;
        field.addEventListener("change", updateSignature);
    });

    populateDobYears();
    updateHiddenDob();

    enableOnScroll(termsScrollBox, termsCheckbox, termsStatus, "Read");
    enableOnScroll(gdprScrollBox, gdprCheckbox, gdprStatus, "Read");

    updatePreview();
    updateSignature();
});

// Change Details live summary and address lookup
document.addEventListener("DOMContentLoaded", function () {
    const changeDetailsForm = document.getElementById("change-details-form");

    if (!changeDetailsForm) return;

    function bindLiveText(inputId, outputId) {
        const input = document.getElementById(inputId);
        const output = document.getElementById(outputId);

        if (!input || !output) return;

        function updateValue() {
            output.textContent = input.value.trim() || "—";
        }

        input.addEventListener("input", updateValue);
        input.addEventListener("change", updateValue);
        updateValue();
    }

    bindLiveText("email", "summary-email");
    bindLiveText("phone", "summary-phone");
    bindLiveText("address_line_1", "summary-address-line-1");
    bindLiveText("address_line_2", "summary-address-line-2");
    bindLiveText("town_city", "summary-town-city");
    bindLiveText("county", "summary-county");
    bindLiveText("postcode", "summary-postcode");

    bindLiveText("contact_name", "summary-contact-name");
    bindLiveText("contact_email", "summary-contact-email");

    bindLiveText("department", "summary-department");
    bindLiveText("job_title", "summary-job-title"); 

    const postcode = document.getElementById("postcode");
    const findAddressBtn = document.getElementById("change-details-find-address-btn");
    const addressSelect = document.getElementById("change-details-address-select");
    const addressLookupMessage = document.getElementById("change-details-address-lookup-message");

    const addressLine1 = document.getElementById("address_line_1");
    const addressLine2 = document.getElementById("address_line_2");
    const townCity = document.getElementById("town_city");
    const county = document.getElementById("county");

    function populateAddressFields(address) {
        if (!address) return;

        if (addressLine1) {
            addressLine1.value = address.address_line_1 || "";
            addressLine1.dispatchEvent(new Event("input"));
        }

        if (addressLine2) {
            addressLine2.value = address.address_line_2 || "";
            addressLine2.dispatchEvent(new Event("input"));
        }

        if (townCity) {
            townCity.value = address.town_city || "";
            townCity.dispatchEvent(new Event("input"));
        }

        if (county) {
            county.value = address.county || "";
            county.dispatchEvent(new Event("input"));
        }

        if (postcode) {
            postcode.value = address.postcode || postcode.value || "";
            postcode.dispatchEvent(new Event("input"));
        }
    }

    async function lookupDemoAddresses() {
        if (!postcode || !addressSelect || !addressLookupMessage) return;

        const postcodeValue = postcode.value.trim();

        addressLookupMessage.textContent = "";
        addressLookupMessage.classList.remove("success", "error");
        addressSelect.innerHTML = '<option value="">Select an address</option>';

        if (!postcodeValue) {
            addressLookupMessage.textContent = "Please enter a postcode.";
            addressLookupMessage.classList.add("error");
            return;
        }

        try {
            const response = await fetch("/register/student/address-lookup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ postcode: postcodeValue })
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                addressLookupMessage.textContent =
                    result.message || "No demo addresses found for that postcode.";
                addressLookupMessage.classList.add("error");
                return;
            }

            result.addresses.forEach((address, index) => {
                const option = document.createElement("option");
                option.value = String(index);
                option.textContent = address.label;
                option.dataset.address = JSON.stringify(address);
                addressSelect.appendChild(option);
            });

            addressLookupMessage.textContent =
                result.message || `${result.addresses.length} address(es) found.`;
            addressLookupMessage.classList.add("success");
        } catch (error) {
            addressLookupMessage.textContent = "Unable to look up demo addresses right now.";
            addressLookupMessage.classList.add("error");
        }
    }

    if (findAddressBtn) {
        findAddressBtn.addEventListener("click", lookupDemoAddresses);
    }

    if (addressSelect) {
        addressSelect.addEventListener("change", function () {
            const selectedOption = addressSelect.options[addressSelect.selectedIndex];
            if (!selectedOption || !selectedOption.dataset.address) return;

            try {
                const address = JSON.parse(selectedOption.dataset.address);
                populateAddressFields(address);
            } catch (error) {
                // no-op
            }
        });
    }
});