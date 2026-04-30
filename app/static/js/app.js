document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", () => {
            const btn = form.querySelector("button");
            if (btn) {
                btn.dataset.originalText = btn.innerText;
                btn.innerText = "Processing...";
                btn.disabled = true;
            }
        });
    });
});

function updateWaterUsagePreview() {
    const previous = document.getElementById("previous_reading");
    const current = document.getElementById("current_reading");
    const preview = document.getElementById("usage_preview");

    if (!previous || !current || !preview) return;

    const previousValue = parseFloat(previous.value || 0);
    const currentValue = parseFloat(current.value || 0);
    const usage = currentValue - previousValue;

    if (usage < 0) {
        preview.textContent = "Invalid reading";
        preview.classList.remove("text-cyan-800");
        preview.classList.add("text-red-700");
    } else {
        preview.textContent = usage.toFixed(2) + " units";
        preview.classList.remove("text-red-700");
        preview.classList.add("text-cyan-800");
    }
}

document.addEventListener("input", (event) => {
    if (event.target && (event.target.id === "previous_reading" || event.target.id === "current_reading")) {
        updateWaterUsagePreview();
    }
});
