document.addEventListener("DOMContentLoaded", () => {
    initialiseEmployerRegistrationPage();
});

/**
 * Employer registration page controller.
 *
 * This file owns the employer registration journey, including:
 * - access code validation
 * - employer name and allowed domain loading
 * - work email builder
 * - declaration status updates
 * - scroll-gated document acknowledgement
 */
function initialiseEmployerRegistrationPage() {
    const form = document.getElementById("employer-registration-form");

    if (!form) {
        return;
    }

    const elements = getEmployerRegistrationElements();

    bindEmployerRegistrationEvents(elements);
    initialiseEmployerRegistrationState(elements);
}

/**
 * Collects all DOM references used by the employer registration page.
 */
function getEmployerRegistrationElements() {
    const scrollDocs = document.querySelectorAll(".scroll-doc-box .scroll-doc");

    return {
        accessCode: document.getElementById("access_code"),
        accessCodeMessage: document.getElementById("access-code-message"),
        employerName: document.getElementById("employer_name"),

        emailUsername: document.getElementById("email_username"),
        emailDomain: document.getElementById("email_domain"),
        workEmail: document.getElementById("work_email"),

        termsCheckbox: document.getElementById("terms_agreed"),
        gdprCheckbox: document.getElementById("gdpr_agreed"),

        termsStatus: document.getElementById("terms-status"),
        gdprStatus: document.getElementById("gdpr-status"),

        termsScrollBox: scrollDocs[0] || null,
        gdprScrollBox: scrollDocs[1] || null
    };
}

/**
 * Sets up the initial page state.
 */
function initialiseEmployerRegistrationState(elements) {
    if (elements.emailDomain) {
        elements.emailDomain.disabled = true;
    }

    updateDeclarationStatus(elements);

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
 * Binds all page events for employer registration.
 */
function bindEmployerRegistrationEvents(elements) {
    if (elements.accessCode) {
        bindAccessCodeLookup({
            accessCodeInput: elements.accessCode,
            lookup: async () => {
                await lookupAccessCode({
                    endpoint: "/register/employer/access-code-lookup",
                    accessCodeInput: elements.accessCode,
                    messageElement: elements.accessCodeMessage,
                    reset: () => {
                        resetEmployerAccessFeedback(elements);
                    },
                    onSuccess: (result) => {
                        if (elements.employerName) {
                            elements.employerName.value = result.employer_name || "";
                        }

                        populateEmployerDomains(elements, result.allowed_domains || []);
                        buildEmployerEmail(elements);
                    },
                    onFailure: () => {
                        buildEmployerEmail(elements);
                    }
                });
            }
        });
    }

    if (elements.emailUsername) {
        elements.emailUsername.addEventListener("input", () => {
            buildEmployerEmail(elements);
        });
    }

    if (elements.emailDomain) {
        elements.emailDomain.addEventListener("change", () => {
            buildEmployerEmail(elements);
        });
    }

    [elements.termsCheckbox, elements.gdprCheckbox].forEach((field) => {
        if (!field) {
            return;
        }

        field.addEventListener("change", () => {
            updateDeclarationStatus(elements);
        });
    });
}

/**
 * Clears employer lookup feedback and resets domain/email-related fields.
 */
function resetEmployerAccessFeedback(elements) {
    if (elements.employerName) {
        elements.employerName.value = "";
    }

    if (elements.accessCodeMessage) {
        elements.accessCodeMessage.textContent = "";
        elements.accessCodeMessage.classList.remove("success", "error");
    }

    if (elements.emailDomain) {
        elements.emailDomain.innerHTML = '<option value="">Select domain</option>';
        elements.emailDomain.disabled = true;
    }

    if (elements.workEmail) {
        elements.workEmail.value = "";
    }
}

/**
 * Populates the domain dropdown using the domains returned by the server.
 */
function populateEmployerDomains(elements, domains) {
    if (!elements.emailDomain) {
        return;
    }

    elements.emailDomain.innerHTML = '<option value="">Select domain</option>';

    domains.forEach((domain) => {
        const option = document.createElement("option");
        option.value = domain;
        option.textContent = `@${domain}`;
        elements.emailDomain.appendChild(option);
    });

    elements.emailDomain.disabled = domains.length === 0;
}

/**
 * Builds the full work email address from the selected username and domain.
 */
function buildEmployerEmail(elements) {
    if (!elements.emailUsername || !elements.emailDomain || !elements.workEmail) {
        return;
    }

    const username = elements.emailUsername.value.trim().toLowerCase();
    const domain = elements.emailDomain.value.trim().toLowerCase();

    elements.workEmail.value = username && domain ? `${username}@${domain}` : "";
}

/**
 * Updates the declaration status labels based on the current checkbox state.
 */
function updateDeclarationStatus(elements) {
    if (elements.termsStatus && elements.termsCheckbox) {
        elements.termsStatus.textContent =
            elements.termsCheckbox.checked ? "Accepted" : "Please review below";
    }

    if (elements.gdprStatus && elements.gdprCheckbox) {
        elements.gdprStatus.textContent =
            elements.gdprCheckbox.checked ? "Accepted" : "Please review below";
    }
}