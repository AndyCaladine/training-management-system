/**
 * Shared access code lookup helper.
 *
 * Why this exists:
 * Both student and employer registration flows validate an access code
 * against the server and then update the page with the result.
 *
 * This helper keeps the network request, success handling, failure handling,
 * and feedback message behaviour consistent across those pages.
 *
 * Expected usage:
 * lookupAccessCode({
 *     endpoint: "/register/student/access-code-lookup",
 *     accessCodeInput,
 *     messageElement,
 *     reset: () => { ... },
 *     onSuccess: (result) => { ... },
 *     onFailure: () => { ... }
 * });
 */
async function lookupAccessCode({
    endpoint,
    accessCodeInput,
    messageElement,
    reset,
    onSuccess,
    onFailure
}) {
    if (!endpoint || !accessCodeInput || !messageElement) {
        return;
    }

    const code = accessCodeInput.value.trim();

    if (typeof reset === "function") {
        reset();
    }

    messageElement.textContent = "";
    messageElement.classList.remove("success", "error");

    if (!code) {
        return;
    }

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ access_code: code })
        });

        const result = await response.json();

        if (response.ok && result.valid) {
            if (typeof onSuccess === "function") {
                onSuccess(result);
            }

            messageElement.textContent = result.message || "Access code accepted.";
            messageElement.classList.add("success");
            return;
        }

        if (typeof onFailure === "function") {
            onFailure(result);
        }

        messageElement.textContent = result.message || "Access code not recognised.";
        messageElement.classList.add("error");
    } catch (error) {
        if (typeof onFailure === "function") {
            onFailure();
        }

        messageElement.textContent = "Unable to validate access code right now.";
        messageElement.classList.add("error");
    }
}

/**
 * Adds a debounced access code lookup to an input.
 *
 * Why this exists:
 * Both registration journeys currently use the same interaction pattern:
 * - look up shortly after typing stops
 * - also validate on blur
 *
 * This wrapper keeps that setup consistent and readable in the page files.
 */
function bindAccessCodeLookup({
    accessCodeInput,
    delay = 400,
    lookup
}) {
    if (!accessCodeInput || typeof lookup !== "function") {
        return;
    }

    let timerId;

    accessCodeInput.addEventListener("input", () => {
        clearTimeout(timerId);

        timerId = setTimeout(() => {
            lookup();
        }, delay);
    });

    accessCodeInput.addEventListener("blur", lookup);
}