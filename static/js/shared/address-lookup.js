/**
 * Shared demo address lookup helper.
 *
 * Why this exists:
 * Multiple forms use the same postcode-to-address lookup flow:
 * - submit the postcode to the backend
 * - populate a select list of available addresses
 * - display success or failure feedback
 *
 * Centralising this keeps the behaviour consistent and avoids repeating
 * the same fetch and DOM update logic in several page files.
 */
async function lookupDemoAddresses({
    postcodeInput,
    selectElement,
    messageElement,
    endpoint = "/register/student/address-lookup"
}) {
    if (!postcodeInput || !selectElement || !messageElement) {
        return;
    }

    const postcode = postcodeInput.value.trim();

    messageElement.textContent = "";
    messageElement.classList.remove("success", "error");
    selectElement.innerHTML = '<option value="">Select an address</option>';

    if (!postcode) {
        messageElement.textContent = "Please enter a postcode.";
        messageElement.classList.add("error");
        return;
    }

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ postcode })
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            messageElement.textContent =
                result.message || "No demo addresses found for that postcode.";
            messageElement.classList.add("error");
            return;
        }

        result.addresses.forEach((address, index) => {
            const option = document.createElement("option");
            option.value = String(index);
            option.textContent = address.label;
            option.dataset.address = JSON.stringify(address);
            selectElement.appendChild(option);
        });

        messageElement.textContent =
            result.message || `${result.addresses.length} address(es) found.`;
        messageElement.classList.add("success");
    } catch (error) {
        messageElement.textContent = "Unable to look up demo addresses right now.";
        messageElement.classList.add("error");
    }
}

/**
 * Reads the currently selected address option and returns the parsed object.
 *
 * Returns null if nothing valid is selected.
 */
function getSelectedAddress(selectElement) {
    if (!selectElement) {
        return null;
    }

    const selectedOption = selectElement.options[selectElement.selectedIndex];

    if (!selectedOption || !selectedOption.dataset.address) {
        return null;
    }

    try {
        return JSON.parse(selectedOption.dataset.address);
    } catch (error) {
        return null;
    }
}

/**
 * Populates common address fields using a selected address object.
 *
 * This is shared because both student registration and change details
 * use the same field naming convention.
 */
function populateStandardAddressFields({
    address,
    addressLine1Input,
    addressLine2Input,
    townCityInput,
    countyInput,
    postcodeInput,
    dispatchInputEvent = false
}) {
    if (!address) {
        return;
    }

    const fieldMappings = [
        { element: addressLine1Input, value: address.address_line_1 || "" },
        { element: addressLine2Input, value: address.address_line_2 || "" },
        { element: townCityInput, value: address.town_city || "" },
        { element: countyInput, value: address.county || "" },
        { element: postcodeInput, value: address.postcode || postcodeInput?.value || "" }
    ];

    fieldMappings.forEach(({ element, value }) => {
        if (!element) {
            return;
        }

        element.value = value;

        if (dispatchInputEvent) {
            element.dispatchEvent(new Event("input"));
        }
    });
}