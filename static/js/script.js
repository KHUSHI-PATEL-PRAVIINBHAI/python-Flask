document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("uploadForm");
    const statusBox = document.getElementById("statusBox");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        statusBox.innerHTML = "🔍 Recognizing...";
        statusBox.style.backgroundColor = "#fff4cc";

        try {
            const response = await fetch("/login", {
                method: "POST",
                body: formData,
            });

            const text = await response.text();
            if (text.includes("Welcome")) {
                statusBox.innerHTML = `✅ ${text}`;
                statusBox.style.backgroundColor = "#d1f7c4";
            } else {
                statusBox.innerHTML = "❌ Face not recognized. Access Denied.";
                statusBox.style.backgroundColor = "#ffe5e5";
            }
        } catch (err) {
            console.error("Error:", err);
            statusBox.innerHTML = "⚠️ Something went wrong. Try again.";
            statusBox.style.backgroundColor = "#ffdddd";
        }
    });
});