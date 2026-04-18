document.addEventListener("DOMContentLoaded", () => {
    initialiseChangeDetailsPage();
});

/**
 * Change details page controller.
 *
 * This file owns:
 * - live summary mirroring for profile/contact fields
 * - demo address lookup
 * - populating standard address fields from the selected address
 * - employer-specific email username/domain handling
 */
function initialiseChangeDetailsPage() {
    const form = document.getElementById("change-details-form");

    if (!form) {
        return;
    }

    const elements = getChangeDetailsElements();

    bindLiveSummaryFields(elements);
    bindChangeDetailsEvents(elements);
    initialiseEmployerChangeDetails();
}

/**
 * Collects all DOM references used by the change details page.
 */
function getChangeDetailsElements() {
    return {
        email: document.getElementById("email"),
        phone: document.getElementById("phone"),
        addressLine1: document.getElementById("address_line_1"),
        addressLine2: document.getElementById("address_line_2"),
        townCity: document.getElementById("town_city"),
        county: document.getElementById("county"),
        postcode: document.getElementById("postcode"),

        department: document.getElementById("department"),
        jobTitle: document.getElementById("job_title"),

        summaryEmail: document.getElementById("summary-email"),
        summaryPhone: document.getElementById("summary-phone"),
        summaryAddressLine1: document.getElementById("summary-address-line-1"),
        summaryAddressLine2: document.getElementById("summary-address-line-2"),
        summaryTownCity: document.getElementById("summary-town-city"),
        summaryCounty: document.getElementById("summary-county"),
        summaryPostcode: document.getElementById("summary-postcode"),
        summaryDepartment: document.getElementById("summary-department"),
        summaryJobTitle: document.getElementById("summary-job-title"),

        findAddressButton: document.getElementById("change-details-find-address-btn"),
        addressSelect: document.getElementById("change-details-address-select"),
        addressLookupMessage: document.getElementById("change-details-address-lookup-message")
    };
}

/**
 * Binds pairs of inputs and summary outputs so the preview updates live as the user types.
 */
function bindLiveSummaryFields(elements) {
    const mappings = [
        { input: elements.email, output: elements.summaryEmail },
        { input: elements.phone, output: elements.summaryPhone },
        { input: elements.addressLine1, output: elements.summaryAddressLine1 },
        { input: elements.addressLine2, output: elements.summaryAddressLine2 },
        { input: elements.townCity, output: elements.summaryTownCity },
        { input: elements.county, output: elements.summaryCounty },
        { input: elements.postcode, output: elements.summaryPostcode },
        { input: elements.department, output: elements.summaryDepartment },
        { input: elements.jobTitle, output: elements.summaryJobTitle }
    ];

    mappings.forEach(({ input, output }) => {
        bindLiveTextField(input, output);
    });
}

/**
 * Attaches one input to one summary output.
 */
function bindLiveTextField(input, output) {
    if (!input || !output) {
        return;
    }

    function updateValue() {
        output.textContent = input.value.trim() || "—";
    }

    input.addEventListener("input", updateValue);
    input.addEventListener("change", updateValue);

    updateValue();
}

/**
 * Binds address lookup interactions for the page.
 */
function bindChangeDetailsEvents(elements) {
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
                postcodeInput: elements.postcode,
                dispatchInputEvent: true
            });
        });
    }
}

/**
 * Employer change details controller.
 *
 * Why this exists:
 * This handles the employer-specific behaviour on the change details page,
 * including:
 * - splitting the stored email into username + domain
 * - selecting the current allowed domain from the server-rendered list
 * - rebuilding the full email address
 * - keeping the live summary in sync
 *
 * This mirrors the behaviour used in employer registration so the
 * experience is consistent across the application.
 */
function initialiseEmployerChangeDetails() {
    const firstName = document.getElementById("first_name");
    const lastName = document.getElementById("last_name");
    const emailUsername = document.getElementById("email_username");
    const emailDomain = document.getElementById("email_domain");
    const emailHidden = document.getElementById("email");

    // Exit early if this is not the employer version of the page
    if (!firstName || !lastName || !emailUsername || !emailDomain || !emailHidden) {
        return;
    }

    // Pre-populate email fields from stored value
    populateEmployerEmailFields(emailHidden.value, emailUsername);

    // Select current domain from server-rendered list
    selectCurrentEmployerDomain(emailDomain, emailHidden.value);

    // Bind input events
    firstName.addEventListener("input", updateEmployerSummary);
    lastName.addEventListener("input", updateEmployerSummary);

    emailUsername.addEventListener("input", () => {
        buildEmployerChangeEmail(emailUsername, emailDomain, emailHidden);
        updateEmployerSummary();
    });

    emailDomain.addEventListener("change", () => {
        buildEmployerChangeEmail(emailUsername, emailDomain, emailHidden);
        updateEmployerSummary();
    });

    // Initial summary state
    updateEmployerSummary();
}

/**
 * Splits an existing email into username and prepares the field.
 *
 * Example:
 * "john.smith@company.com" → username = "john.smith"
 */
function populateEmployerEmailFields(currentEmail, emailUsername) {
    if (!currentEmail || !currentEmail.includes("@")) {
        return;
    }

    const [username] = currentEmail.split("@");
    emailUsername.value = username || "";
}

/**
 * Selects the current saved email domain from the dropdown.
 *
 * Why this exists:
 * The allowed domains are rendered by Flask from the database,
 * so the page only needs to match the current saved email against
 * the existing options.
 */
function selectCurrentEmployerDomain(emailDomain, currentEmail) {
    if (!emailDomain || !currentEmail || !currentEmail.includes("@")) {
        return;
    }

    const currentDomain = currentEmail.split("@")[1].toLowerCase();
    emailDomain.value = currentDomain;
}

/**
 * Builds the full email address from username and selected domain.
 *
 * Example:
 * username = "john.smith"
 * domain = "company.com"
 * result = "john.smith@company.com"
 */
function buildEmployerChangeEmail(emailUsername, emailDomain, emailHidden) {
    const username = emailUsername.value.trim().toLowerCase();
    const domain = emailDomain.value.trim().toLowerCase();

    emailHidden.value = username && domain ? `${username}@${domain}` : "";
}

/**
 * Updates the employer live summary panel with current values.
 *
 * This keeps the right-hand summary card in sync with user input.
 */
function updateEmployerSummary() {
    const firstName = document.getElementById("first_name");
    const lastName = document.getElementById("last_name");
    const emailHidden = document.getElementById("email");

    const summaryFirstName = document.getElementById("summary-first-name");
    const summaryLastName = document.getElementById("summary-last-name");
    const summaryEmail = document.getElementById("summary-email");

    if (summaryFirstName) {
        summaryFirstName.textContent = firstName?.value.trim() || "—";
    }

    if (summaryLastName) {
        summaryLastName.textContent = lastName?.value.trim() || "—";
    }

    if (summaryEmail) {
        summaryEmail.textContent = emailHidden?.value.trim() || "—";
    }
}