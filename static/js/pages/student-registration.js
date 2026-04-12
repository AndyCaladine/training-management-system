document.addEventListener("DOMContentLoaded", () => {
    initialiseStudentRegistrationPage();
});

/**
 * Student registration page controller.
 *
 * This file owns the student registration experience, including:
 * - access code validation
 * - training agreement preview updates
 * - duration and end-date calculation
 * - date of birth assembly
 * - scroll-gated declarations
 * - demo address lookup
 * - signature preview
 *
 * Shared utilities are kept in static/js/shared/.
 * Page-specific orchestration stays here so the flow remains easy to follow.
 */
function initialiseStudentRegistrationPage() {
    const form = document.getElementById("student-registration-form");

    if (!form) {
        return;
    }

    const elements = getStudentRegistrationElements();

    bindStudentRegistrationEvents(elements);
    initialiseStudentRegistrationState(elements);
}

/**
 * Collects all DOM references used by the student registration page.
 * Keeping them in one place makes the rest of the file much easier to scan.
 */
function getStudentRegistrationElements() {
    return {
        accessCode: document.getElementById("access_code"),
        accessCodeMessage: document.getElementById("access-code-message"),

        firstName: document.getElementById("first_name"),
        lastName: document.getElementById("last_name"),
        employerName: document.getElementById("employer_name"),
        startDate: document.getElementById("start_date"),
        years: document.getElementById("years"),
        months: document.getElementById("months"),
        days: document.getElementById("days"),

        postcode: document.getElementById("postcode"),
        findAddressButton: document.getElementById("find-address-btn"),
        addressSelect: document.getElementById("address_select"),
        addressLookupMessage: document.getElementById("address-lookup-message"),

        addressLine1: document.getElementById("address_line_1"),
        addressLine2: document.getElementById("address_line_2"),
        townCity: document.getElementById("town_city"),
        county: document.getElementById("county"),

        dobDay: document.getElementById("dob_day"),
        dobMonth: document.getElementById("dob_month"),
        dobYear: document.getElementById("dob_year"),
        dobHidden: document.getElementById("date_of_birth"),
        dobYearOptions: document.getElementById("dob-year-options"),

        manualAddressToggle: document.getElementById("manual-address-toggle"),
        manualAddressFields: document.getElementById("manual-address-fields"),

        summaryName: document.getElementById("summary-name"),
        summaryEmployer: document.getElementById("summary-employer"),
        summaryStart: document.getElementById("summary-start"),
        summaryDuration: document.getElementById("summary-duration"),
        summaryEnd: document.getElementById("summary-end"),

        agreementPreviewText: document.getElementById("agreement-preview-text"),

        termsStudentName: document.getElementById("terms-student-name"),
        termsEmployerName: document.getElementById("terms-employer-name"),
        termsStartDate: document.getElementById("terms-start-date"),
        termsDuration: document.getElementById("terms-duration"),
        termsEndDate: document.getElementById("terms-end-date"),

        termsScrollBox: document.getElementById("terms-scroll-box"),
        gdprScrollBox: document.getElementById("gdpr-scroll-box"),

        termsCheckbox: document.getElementById("terms_agreed"),
        gdprCheckbox: document.getElementById("gdpr_agreed"),

        termsStatus: document.getElementById("terms-status"),
        gdprStatus: document.getElementById("gdpr-status"),

        signatureName: document.getElementById("signature-name"),
        signatureDate: document.getElementById("signature-date")
    };
}

/**
 * Sets the page to a clean, ready state on first load.
 */
function initialiseStudentRegistrationState(elements) {
    populateDobYears(elements);
    updateHiddenDob(elements);
    updateTrainingPreview(elements);
    updateSignature(elements);

    initialiseScrollGate({
        scrollBox: elements.termsScrollBox,
        checkbox: elements.termsCheckbox,
        statusElement: elements.termsStatus,
        completeText: "Read"
    });

    initialiseScrollGate({
        scrollBox: elements.gdprScrollBox,
        checkbox: elements.gdprCheckbox,
        statusElement: elements.gdprStatus,
        completeText: "Read"
    });
}

/**
 * Binds all page events in one place so the registration flow is easy to trace.
 */
function bindStudentRegistrationEvents(elements) {
    if (elements.manualAddressToggle) {
        elements.manualAddressToggle.addEventListener("click", () => {
            toggleManualAddress(elements);
        });
    }

    if (elements.findAddressButton) {
        elements.findAddressButton.addEventListener("click", async () => {
            await lookupDemoAddresses({
                postcodeInput: elements.postcode,
                selectElement: elements.addressSelect,
                messageElement: elements.addressLookupMessage
            });
        });
    }

    if (elements.addressSelect) {
        elements.addressSelect.addEventListener("change", () => {
            const selectedAddress = getSelectedAddress(elements.addressSelect);

            populateStandardAddressFields({
                address: selectedAddress,
                addressLine1Input: elements.addressLine1,
                addressLine2Input: elements.addressLine2,
                townCityInput: elements.townCity,
                countyInput: elements.county,
                postcodeInput: elements.postcode
            });

            if (
                elements.manualAddressFields &&
                !elements.manualAddressFields.classList.contains("show")
            ) {
                elements.manualAddressFields.classList.add("show");
            }

            if (elements.manualAddressToggle) {
                elements.manualAddressToggle.textContent = "Hide manual address entry";
            }
        });
    }

    if (elements.accessCode) {
        bindAccessCodeLookup({
            accessCodeInput: elements.accessCode,
            lookup: async () => {
                await lookupAccessCode({
                    endpoint: "/register/student/access-code-lookup",
                    accessCodeInput: elements.accessCode,
                    messageElement: elements.accessCodeMessage,
                    reset: () => {
                        if (elements.employerName) {
                            elements.employerName.value = "";
                        }
                    },
                    onSuccess: (result) => {
                        if (elements.employerName) {
                            elements.employerName.value = result.employer_name || "";
                        }

                        updateTrainingPreview(elements);
                    },
                    onFailure: () => {
                        if (elements.employerName) {
                            elements.employerName.value = "";
                        }

                        updateTrainingPreview(elements);
                    }
                });
            }
        });
    }

    [
        elements.firstName,
        elements.lastName,
        elements.employerName,
        elements.startDate,
        elements.years,
        elements.months,
        elements.days
    ].forEach((field) => {
        if (!field) {
            return;
        }

        field.addEventListener("input", () => {
            updateTrainingPreview(elements);
            updateSignature(elements);
        });

        field.addEventListener("change", () => {
            updateTrainingPreview(elements);
            updateSignature(elements);
        });
    });

    [elements.dobDay, elements.dobMonth, elements.dobYear].forEach((field) => {
        if (!field) {
            return;
        }

        field.addEventListener("input", () => {
            updateHiddenDob(elements);
        });

        field.addEventListener("change", () => {
            updateHiddenDob(elements);
        });
    });

    [elements.termsCheckbox, elements.gdprCheckbox].forEach((field) => {
        if (!field) {
            return;
        }

        field.addEventListener("change", () => {
            updateSignature(elements);
        });
    });
}

/**
 * Formats a backend date string into a friendly UK display date.
 */
function formatDisplayDate(dateString) {
    if (!dateString) {
        return "—";
    }

    const date = new Date(`${dateString}T00:00:00`);

    if (Number.isNaN(date.getTime())) {
        return "—";
    }

    return date.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "long",
        year: "numeric"
    });
}

/**
 * Populates the year datalist used by the date of birth fields.
 */
function populateDobYears(elements) {
    if (!elements.dobYearOptions) {
        return;
    }

    const currentYear = new Date().getFullYear();
    elements.dobYearOptions.innerHTML = "";

    for (let year = 1901; year <= currentYear; year += 1) {
        const option = document.createElement("option");
        option.value = String(year);
        elements.dobYearOptions.appendChild(option);
    }
}

/**
 * Converts a month name into a two-digit month number.
 */
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

/**
 * Builds the hidden ISO date of birth value from the visible day, month, and year inputs.
 * This keeps the user-facing inputs flexible while still submitting a backend-friendly value.
 */
function updateHiddenDob(elements) {
    const { dobDay, dobMonth, dobYear, dobHidden } = elements;

    if (!dobDay || !dobMonth || !dobYear || !dobHidden) {
        return;
    }

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
        return;
    }

    dobHidden.value = "";
}

/**
 * Builds a friendly training duration string from the selected years, months, and days.
 */
function buildDurationText(elements) {
    const years = parseInt(elements.years?.value || 0, 10);
    const months = parseInt(elements.months?.value || 0, 10);
    const days = parseInt(elements.days?.value || 0, 10);

    const parts = [];

    if (years > 0) {
        parts.push(`${years} year${years !== 1 ? "s" : ""}`);
    }

    if (months > 0) {
        parts.push(`${months} month${months !== 1 ? "s" : ""}`);
    }

    if (days > 0) {
        parts.push(`${days} day${days !== 1 ? "s" : ""}`);
    }

    return parts.length ? parts.join(", ") : "—";
}

/**
 * Calculates the agreement end date based on the selected start date and duration.
 */
function calculateEndDate(elements) {
    if (!elements.startDate || !elements.startDate.value) {
        return "—";
    }

    const date = new Date(`${elements.startDate.value}T00:00:00`);
    const years = parseInt(elements.years?.value || 0, 10);
    const months = parseInt(elements.months?.value || 0, 10);
    const days = parseInt(elements.days?.value || 0, 10);

    if (Number.isNaN(date.getTime())) {
        return "—";
    }

    if (years === 0 && months === 0 && days === 0) {
        return "—";
    }

    date.setFullYear(date.getFullYear() + years);
    date.setMonth(date.getMonth() + months);
    date.setDate(date.getDate() + days);

    return date.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "long",
        year: "numeric"
    });
}

/**
 * Updates the live agreement summary and declaration preview text.
 */
function updateTrainingPreview(elements) {
    const fullName =
        `${elements.firstName?.value || ""} ${elements.lastName?.value || ""}`.trim() || "—";

    const employer = elements.employerName?.value?.trim() || "—";
    const formattedStart = formatDisplayDate(elements.startDate?.value || "");
    const durationText = buildDurationText(elements);
    const endDateText = calculateEndDate(elements);

    if (elements.summaryName) {
        elements.summaryName.textContent = fullName;
    }

    if (elements.summaryEmployer) {
        elements.summaryEmployer.textContent = employer;
    }

    if (elements.summaryStart) {
        elements.summaryStart.textContent = formattedStart;
    }

    if (elements.summaryDuration) {
        elements.summaryDuration.textContent = durationText;
    }

    if (elements.summaryEnd) {
        elements.summaryEnd.textContent = endDateText;
    }

    if (elements.termsStudentName) {
        elements.termsStudentName.textContent = fullName !== "—" ? fullName : "the student";
    }

    if (elements.termsEmployerName) {
        elements.termsEmployerName.textContent = employer !== "—" ? employer : "the employer";
    }

    if (elements.termsStartDate) {
        elements.termsStartDate.textContent =
            formattedStart !== "—" ? formattedStart : "the selected start date";
    }

    if (elements.termsDuration) {
        elements.termsDuration.textContent =
            durationText !== "—" ? durationText : "the selected duration";
    }

    if (elements.termsEndDate) {
        elements.termsEndDate.textContent =
            endDateText !== "—" ? endDateText : "the calculated end date";
    }

    if (elements.agreementPreviewText) {
        elements.agreementPreviewText.textContent =
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

/**
 * Updates the electronic signature preview once both declarations are accepted.
 */
function updateSignature(elements) {
    const fullName =
        `${elements.firstName?.value || ""} ${elements.lastName?.value || ""}`.trim();

    if (elements.termsCheckbox?.checked && elements.gdprCheckbox?.checked && fullName) {
        const today = new Date().toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "long",
            year: "numeric"
        });

        if (elements.signatureName) {
            elements.signatureName.textContent = fullName;
        }

        if (elements.signatureDate) {
            elements.signatureDate.textContent = `Signed electronically on ${today}`;
        }

        return;
    }

    if (elements.signatureName) {
        elements.signatureName.textContent = "Awaiting agreement";
    }

    if (elements.signatureDate) {
        elements.signatureDate.textContent =
            "Date will appear once declarations are accepted";
    }
}

/**
 * Shows or hides the manual address entry section.
 */
function toggleManualAddress(elements) {
    if (!elements.manualAddressFields) {
        return;
    }

    elements.manualAddressFields.classList.toggle("show");

    if (elements.manualAddressToggle) {
        elements.manualAddressToggle.textContent =
            elements.manualAddressFields.classList.contains("show")
                ? "Hide manual address entry"
                : "Enter address manually";
    }
}