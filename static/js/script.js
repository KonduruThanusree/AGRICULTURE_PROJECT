
async function api(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || "Request failed");
    }

    return data;
}

function postJSON(url, body) {
    return api(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    });
}

function formToObject(form) {
    const result = {};

    new FormData(form).forEach((value, key) => {
        result[key] = value;
    });

    return result;
}

function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function showError(element, error) {
    element.innerHTML = `
        <p style="color:red;">
            ${esc(error.message || error)}
        </p>
    `;
}

function bindForm(formId, url, render, outputId = "result") {
    const form = document.getElementById(formId);
    const output = document.getElementById(outputId);

    if (!form || !output) return;

    form.addEventListener("submit", async event => {
        event.preventDefault();

        output.innerHTML = "Please wait...";

        try {
            const data = await postJSON(url, formToObject(form));
            output.innerHTML = render(data);
        } catch (error) {
            showError(output, error);
        }
    });
}
