const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const authMessage = document.getElementById("auth-message");

function showAuthMessage(message, type = "error") {
    if (!authMessage) {
        return;
    }

    authMessage.textContent = message;
    authMessage.className = `form-message ${type}`;
}

function setFormLoading(form, isLoading, message = "") {
    if (!form) {
        return;
    }

    const submitButton = form.querySelector("button[type='submit']");

    if (submitButton) {
        if (!submitButton.dataset.originalText) {
            submitButton.dataset.originalText = submitButton.textContent;
        }

        submitButton.disabled = isLoading;
        submitButton.textContent = isLoading ? "Procesando..." : submitButton.dataset.originalText;
    }

    if (message) {
        showAuthMessage(message, "success");
    }
}

async function postAuth(endpoint, payload) {
    const response = await apiFetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    let data = {};

    try {
        data = await response.json();
    } catch (error) {
        throw new Error("El servidor no respondio en formato valido. Revisa que el backend este corriendo en 127.0.0.1:8000.");
    }

    if (!response.ok) {
        throw new Error(data.detail || "No se pudo completar la accion");
    }

    return data;
}

if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = {
            email: registerForm.email.value.trim(),
            username: registerForm.username.value.trim(),
            password: registerForm.password.value
        };

        try {
            setFormLoading(registerForm, true, "Creando cuenta...");
            const data = await postAuth("/users/register", payload);

            setCurrentSession(data);
            window.location.href = "index.html";
        } catch (error) {
            showAuthMessage(error.message);
        } finally {
            setFormLoading(registerForm, false);
        }
    });
}

if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = {
            email: loginForm.email.value.trim(),
            password: loginForm.password.value
        };

        try {
            setFormLoading(loginForm, true, "Iniciando sesion...");
            const data = await postAuth("/users/login", payload);

            if (!data.success) {
                showAuthMessage(data.message);
                return;
            }

            setCurrentSession(data);
            window.location.href = "index.html";
        } catch (error) {
            showAuthMessage(error.message);
        } finally {
            setFormLoading(loginForm, false);
        }
    });
}
