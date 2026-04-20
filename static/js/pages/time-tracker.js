/*
===========================================================
Time tracker page
-----------------------------------------------------------
Initialises date picker behaviour for the student time
tracker page.
===========================================================
*/

document.addEventListener("DOMContentLoaded", () => {
    initialiseFlatpickrFields([
        {
            selector: ".js-time-tracker-date",
            clickOpens: true,
            allowInput: false
        }
    ]);

    const selectAll = document.getElementById("select_all_entries");
    const checkboxes = document.querySelectorAll(".js-entry-checkbox");

    if (selectAll) {
        selectAll.addEventListener("change", () => {
            checkboxes.forEach(cb => {
                cb.checked = selectAll.checked;
            });
        });
    }
});

checkboxes.forEach(cb => {
    cb.addEventListener("change", () => {
        const allChecked = Array.from(checkboxes).every(c => c.checked);
        selectAll.checked = allChecked;
    });
});

const HOURS_PER_DAY = 7;

function updateSummary() {
    let totalHours = 0;
    let count = 0;

    checkboxes.forEach(cb => {
        if (cb.checked) {
            count++;

            const row = cb.closest("tr");
            const hoursCell = row.children[2];
            const hours = parseFloat(hoursCell.textContent) || 0;

            totalHours += hours;
        }
    });

    if (count === 0) {
        summary.textContent = "No entries selected.";
        return;
    }

    const totalDays = (totalHours / HOURS_PER_DAY).toFixed(2);

    summary.textContent = `${count} entr${count === 1 ? "y" : "ies"} selected • ${totalDays} days`;
}

