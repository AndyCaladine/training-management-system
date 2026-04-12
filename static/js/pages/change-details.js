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
 */
function initialiseChangeDetailsPage() {
    const form = document.getElementById("change-details-form");

    if (!form) {
        return;
    }

    const elements = getChangeDetailsElements();

    bindLiveSummaryFields(elements);
    bindChangeDetailsEvents(elements);
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

        contactName: document.getElementById("contact_name"),
        contactEmail: document.getElementById("contact_email"),

        department: document.getElementById("department"),
        jobTitle: document.getElementById("job_title"),

        summaryEmail: document.getElementById("summary-email"),
        summaryPhone: document.getElementById("summary-phone"),
        summaryAddressLine1: document.getElementById("summary-address-line-1"),
        summaryAddressLine2: document.getElementById("summary-address-line-2"),
        summaryTownCity: document.getElementById("summary-town-city"),
        summaryCounty: document.getElementById("summary-county"),
        summaryPostcode: document.getElementById("summary-postcode"),

        summaryContactName: document.getElementById("summary-contact-name"),
        summaryContactEmail: document.getElementById("summary-contact-email"),

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
        { input: elements.contactName, output: elements.summaryContactName },
        { input: elements.contactEmail, output: elements.summaryContactEmail },
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