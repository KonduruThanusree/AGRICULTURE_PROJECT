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
    return String(value).replace(/[&<>"']/g, c => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[c]);
}

function badge(level) {
    return `<span class="badge">${esc(level)}</span>`;
}

function list(items) {
    return "<ul>" +
        items.map(item => `<li>${esc(item)}</li>`).join("") +
        "</ul>";
}

function showError(element, error) {
    element.innerHTML =
        `<div class="alert alert-red">${esc(error.message)}</div>`;
}

function bindForm(formId, url, render, outputId = "result") {
    const form = document.getElementById(formId);
    const output = document.getElementById(outputId);

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

function optionsHtml(options) {
    return options.map(option => `
        <div class="card">
            <h3>${esc(option.name)}</h3>
            <p>${esc(option.reason)}</p>
            <p>${esc(option.output || "")}</p>
        </div>
    `).join("");
}